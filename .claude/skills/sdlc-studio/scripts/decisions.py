#!/usr/bin/env python3
"""Project decisions log - the canonical home for load-bearing decisions.

`add` appends a decision (auto-numbered `D{NNNN}`, dated) to `sdlc-studio/decisions.md`;
`list` prints the table (optionally filtered by status). Append-only and greppable, so the
project's "spine" - product decisions and implementation conventions - lives in one place
and feeds the handoff context delegated agents read, instead of being pasted per prompt.
Distinct from the sprint per-tranche ledger (`ledger.py`). Pure stdlib.
"""
from __future__ import annotations

import argparse
import ast
import importlib
import json
import re
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lib import sdlc_md  # noqa: E402

SKILL = Path(__file__).resolve().parent.parent
SCRIPTS = Path(__file__).resolve().parent
LOG_REL = "sdlc-studio/decisions.md"
_ROW = re.compile(r"^\|\s*D(\d{4})\s*\|")

# A waiver is an ordinary decision row whose decision cell is the canonical token
# `waiver: <subject>` - so it is greppable and machine-detectable, not narrative. The subject
# names what is intentionally out of scope: a review leg (`leg:tsd`) or, reusably, any rule
# (`rule:engagement-floor`). Lookup is anchored equality on that cell, never a substring, so a
# row that merely mentions the subject is not mistaken for a waiver of it.
WAIVER_PREFIX = "waiver:"
# The four required DOCUMENT legs a `--leg` waiver may name. CODE is deliberately absent: it has
# no single artefact whose presence can be tested, so it is out of scope for the leg-presence gate.
DOC_LEGS = ("prd", "trd", "tsd", "personas")


def _log_path(root: Path) -> Path:
    return Path(root) / LOG_REL


def ensure_log(root: Path | str) -> bool:
    """Create `sdlc-studio/decisions.md` from the template when missing. Idempotent."""
    p = _log_path(Path(root))
    if p.exists():
        return False
    tmpl = SKILL / "templates" / "decisions.md"
    text = re.sub(r"^<!--.*?-->\n+", "", tmpl.read_text(encoding="utf-8"),
                  count=1, flags=re.DOTALL)
    p.parent.mkdir(parents=True, exist_ok=True)
    sdlc_md.atomic_write(p, text)
    return True


def _next_id(text: str) -> str:
    nums = [int(m.group(1)) for m in (_ROW.match(ln) for ln in text.splitlines()) if m]
    return f"D{(max(nums) + 1) if nums else 1:04d}"


# Status is the 4th field when a row is split on unescaped pipes:
# ['', ' Dxxxx ', ' decision ', ' rationale ', ' status ', ' supersedes ', ' date ', '']
_STATUS_CELL = 4
_UNESCAPED_PIPE = re.compile(r"(?<!\\)\|")


def _norm_did(value: str | None) -> str | None:
    """Normalise `D0012` / `0012` / `12` to the canonical `D0012`, or None if not an id.
    Anchored (fullmatch): a value that merely CONTAINS a number (`the 5th one`, `D00121`) is
    not an id, so a fat-fingered --supersedes fails loud rather than silently flipping a
    plausible-but-wrong row."""
    s = (value or "").strip()
    m = re.fullmatch(r"[Dd](\d{4})", s) or re.fullmatch(r"(\d{1,4})", s)
    return f"D{int(m.group(1)):04d}" if m else None


def _flip_to_superseded(lines: list[str], target: str) -> str | None:
    """Flip the `target` decision's Status cell to `superseded`, in place.
    Returns 'changed', 'already' (found but already superseded), or None (id not present)."""
    for i, ln in enumerate(lines):
        m = _ROW.match(ln)
        if not m or f"D{int(m.group(1)):04d}" != target:
            continue
        parts = _UNESCAPED_PIPE.split(ln)
        if len(parts) <= _STATUS_CELL:
            return "already"  # malformed row; leave it, but the id exists
        if parts[_STATUS_CELL].strip() == "superseded":
            return "already"
        parts[_STATUS_CELL] = " superseded "
        lines[i] = "|".join(parts)
        return "changed"
    return None


def add(root: Path | str, decision: str, rationale: str, status: str = "accepted",
        supersedes: str = "", today: str | None = None) -> dict:
    root = Path(root)
    p = _log_path(root)
    # Serialise ensure-log -> read -> allocate -> flip-supersedes -> insert -> write against
    # concurrent `decisions add` calls, so two writers never scan the same table, mint the same
    # D-id and clobber each other's row; the write itself is atomic, so a crash mid-write leaves
    # the previous ledger intact rather than a truncated one. This is a load-bearing shared file
    # (gate/engagement-floor waivers route through it), held to trd.md rule 5 like every other.
    with sdlc_md.allocation_lock(root):
        ensure_log(root)
        lines = p.read_text(encoding="utf-8").splitlines()
        # Supersession is only real if the named decision's own row is flipped to `superseded`
        # in the same edit - otherwise the log carries two contradictory `accepted` rows.
        # Fail loud on an unknown id: without this a typo in --supersedes is silently recorded.
        sup_did = ""
        if supersedes:
            sup_did = _norm_did(supersedes)
            if sup_did is None or _flip_to_superseded(lines, sup_did) is None:
                raise ValueError(
                    f"--supersedes: no decision {supersedes!r} in the log - refusing to record a "
                    "dangling supersession (a typo would otherwise be silently accepted)")
        did = _next_id("\n".join(lines))
        when = today or date.today().isoformat()
        cells = [did, decision.replace("|", "\\|"), rationale.replace("|", "\\|"),
                 status, sup_did or "--", when]
        row = "| " + " | ".join(cells) + " |"
        # insert after the data-table header+separator (the row carrying the ID column)
        hdr = next((i for i, ln in enumerate(lines)
                    if ln.strip().startswith("| ID |") or ln.strip().startswith("| ID|")), None)
        if hdr is None:
            raise ValueError("decisions.md has no decisions table")
        last = max((i for i in range(hdr + 2, len(lines)) if _ROW.match(lines[i])), default=hdr + 1)
        lines.insert(last + 1, row)
        sdlc_md.atomic_write(p, "\n".join(lines) + "\n")
    return {"id": did, "status": status, "date": when}


def _norm_subject(subject: str | None) -> str:
    """Normalise a waiver subject (lowercase, whitespace-stripped) so `LEG:TSD`, ` leg:tsd `
    and `leg:tsd` are the one key - lookup cannot miss on case or padding."""
    return (subject or "").strip().lower()


#: The module-level constant a checker publishes the rules it will honour a waiver for in.
#: Matched by PATTERN over the scripts tree, not against a list of module names typed here: a
#: list would silently exempt the checker added tomorrow, and the whole point of validating a
#: waiver subject is that the vocabulary is complete. Both spellings the tree uses are covered
#: (`WAIVER_RULE` holding a full `rule:x` subject, `WAIVABLE_RULES` holding bare rule names).
RULES_ATTR_RE = re.compile(r"^WAIV(?:ER|ABLE)_RULES?$")
#: The subject families. `leg:` is closed (the four document legs); `rule:` is open and derived.
SUBJECT_RULE = "rule:"


def _modules_declaring_rules(scripts: Path) -> tuple[list[str], list[str]]:
    """(module names assigning a rules constant, module names that could not be read).

    A static parse, so discovery costs no imports and cannot cycle back through this module.
    An unreadable script is returned as UNREADABLE, never as "declares nothing": a file the
    scan could not answer for must widen what the caller admits it does not know.
    """
    declaring, unreadable = [], []
    for path in sorted(scripts.glob("*.py")):
        try:
            tree = ast.parse(path.read_text(encoding="utf-8"))
        except (OSError, SyntaxError, ValueError, UnicodeDecodeError):
            unreadable.append(path.stem)
            continue
        for node in tree.body:
            names = []
            if isinstance(node, ast.Assign):
                names = [t.id for t in node.targets if isinstance(t, ast.Name)]
            elif isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name):
                names = [node.target.id]
            if any(RULES_ATTR_RE.match(n) for n in names):
                declaring.append(path.stem)
                break
    return declaring, unreadable


def waivable_subjects(scripts: Path | None = None) -> tuple[set[str], list[str]]:
    """Every subject a waiver may name, plus the scripts whose declaration could not be read.

    Two families, both derived: `leg:<leg>` from DOC_LEGS, and `rule:<name>` from every sibling
    checker that declares one. The declaring modules are IMPORTED (only those, and only at call
    time) rather than read literally, so a checker may derive its own rule names from its stage
    vocabulary instead of repeating them as a literal - which is the same lesson one rung down.
    """
    scripts = scripts or SCRIPTS
    subjects = {f"leg:{leg}" for leg in DOC_LEGS}
    declaring, unreadable = _modules_declaring_rules(scripts)
    for name in declaring:
        try:
            mod = importlib.import_module(name)
        except Exception:  # noqa: BLE001 - an unimportable checker is UNKNOWN, not empty
            unreadable.append(name)
            continue
        for attr in dir(mod):
            if not RULES_ATTR_RE.match(attr):
                continue
            value = getattr(mod, attr)
            rules = (value,) if isinstance(value, str) else tuple(value or ())
            for rule in rules:
                rule = _norm_subject(str(rule))
                if rule:
                    subjects.add(rule if rule.startswith(SUBJECT_RULE) else SUBJECT_RULE + rule)
    return subjects, unreadable


def subject_error(subject: str, subjects: set[str], unreadable: list[str]) -> str | None:
    """Why `subject` cannot be waived, or None when it can.

    A subject is waivable when it IS a declared subject, or extends one with a scope tail on a
    colon boundary (`rule:engagement-floor:US0100`, `rule:conformance:critiqued:US0103-US0310`) -
    the boundary is what keeps `rule:engagement-floor-v2` a different subject rather than a
    scoped form of `rule:engagement-floor`, exactly as the lookup treats it.
    """
    if subject in subjects or any(subject.startswith(f"{s}:") for s in subjects):
        return None
    short = (f"; note {len(unreadable)} script(s) could not be read for their declared rules "
             f"({', '.join(sorted(unreadable))}), so this list may be incomplete"
             if unreadable else "")
    return (f"unknown waiver subject {subject!r}: no checker declares it, so the waiver would be "
            f"recorded and then do nothing. Known subjects: {', '.join(sorted(subjects))}{short}")


def _scope_tail_error(subject: str) -> str | None:
    """The consumer's scope-tail check, for the subjects that carry one. A rule whose checker
    declares no scope grammar is unaffected - only a `rule:conformance:<stage>:<scope>` tail is
    read here, because that is the one a lane resolves against unit ids."""
    checklist_rule = "rule:sprint-checklist"
    checklist_stem = checklist_rule + ":"
    if subject == checklist_rule:
        # The BARE rule covers nothing: the close reads a waiver per item, so a row naming the
        # family alone records clean and every item stays outstanding.
        try:
            import sprint_report
        except ImportError:  # pragma: no cover - shipped beside this
            return None
        return sprint_report.scope_tail_error("")
    if subject.startswith(checklist_stem):
        try:
            import sprint_report
        except ImportError:  # pragma: no cover - shipped beside this
            return None
        return sprint_report.scope_tail_error(subject[len(checklist_stem):])
    stem = "rule:conformance:"
    if not subject.startswith(stem):
        return None
    _stage, sep, scope = subject[len(stem):].partition(":")
    if not sep:
        return None
    try:
        import conformance
    except ImportError:  # pragma: no cover - the lane is always shipped beside this
        return None
    return conformance.scope_tail_error(scope)


def record_waiver(root: Path | str, subject: str, rationale: str,
                  today: str | None = None, authorised_by: str = "") -> dict:
    """Record a machine-detectable waiver: a decision row `waiver: <subject>`, with the human
    reason in the rationale cell. General over any waivable subject (a review leg `leg:tsd`, or
    a rule `rule:engagement-floor`), so a later gate reuses the same primitive.

    Refused at RECORD time when it would do nothing: an unknown rule (no checker reads that
    subject, so the row is inert), or no rationale (an unexplained waiver is indistinguishable
    from forgetting the rule exists, and nobody can later judge whether it still holds).
    """
    subject = _norm_subject(subject)
    if not subject:
        raise ValueError("a waiver subject must be non-empty (e.g. leg:tsd or rule:<name>)")
    if not str(rationale or "").strip():
        raise ValueError(
            f"a waiver of {subject!r} must record WHY the rule is out of scope here - an "
            "unexplained waiver is indistinguishable from forgetting the rule exists")
    err = subject_error(subject, *waivable_subjects())
    if err:
        raise ValueError(err)
    # ... and the SCOPE TAIL, not only the rule half. Validating the rule and not the scope let
    # `rule:conformance:critiqued:pre-two-role` record clean and cover nothing, so a sprint
    # close stayed blocked by a rule the log said had been waived. The check is the consumer's
    # own (`conformance.scope_tail_error`), imported rather than re-derived - a second reading
    # of the grammar here would be a copy that drifts, and the copy that drifts is the one
    # that accepts what the consumer rejects.
    err = _scope_tail_error(subject)
    if err:
        raise ValueError(err)
    # WHO authorised it, not only why. A waiver is somebody deciding a rule does not apply
    # here; recorded without a name it is a decision with no decider, and the one question a
    # later reader asks - who agreed to this? - has no answer. Required for the families whose
    # rule demands it; recorded whenever supplied.
    who = str(authorised_by or "").strip()
    if not who and subject.startswith("rule:sprint-checklist"):
        raise ValueError(
            f"a waiver of {subject!r} must record WHO authorised it - a compulsory close item "
            "set aside by nobody in particular is a decision with no decider")
    rationale = f"{rationale.strip()} [authorised by: {who}]" if who else rationale
    return add(root, f"{WAIVER_PREFIX} {subject}", rationale, today=today)


_AUTHORISER_RE = re.compile(r"\[authorised by:\s*(.+?)\s*\]\s*$")


def waiver_authoriser(root: Path | str, subject: str) -> str | None:
    """Who authorised the accepted waiver for `subject`, or None when the row records nobody.

    None is a real answer, not a blank: a waiver recorded before the authoriser was required
    genuinely names no one, and reporting that as an empty string would let a reader take it
    for an authoriser whose name happens to be missing."""
    want = f"{WAIVER_PREFIX} {_norm_subject(subject)}"
    for rec in list_decisions(root):
        if rec["status"] == "accepted" and rec["decision"].strip().lower() == want:
            m = _AUTHORISER_RE.search(rec.get("rationale") or "")
            return m.group(1) if m else None
    return None


def waiver_for(root: Path | str, subject: str) -> str | None:
    """The id of the ACCEPTED waiver for `subject`, or None. Anchored equality on the decision
    cell (`waiver: <subject>`), never a substring: a row that merely mentions the subject, or a
    superseded/revisited waiver, does not hold - so a prose reclassification cannot pass as one."""
    want = f"{WAIVER_PREFIX} {_norm_subject(subject)}"
    for rec in list_decisions(root):
        if rec["status"] == "accepted" and rec["decision"].strip().lower() == want:
            return rec["id"]
    return None


def promote(root: Path | str, source: str, decision: str, rationale: str,
            today: str | None = None) -> dict:
    """Promote a resolved PRD open question into the log with a back-link. One
    record, two views: the question stays in `PRD §Open Questions`; this records the
    resolution here as `[from <source>]`, never duplicating it as free text in both."""
    return add(root, decision, f"{rationale} [from {source}]", today=today)


def backfill_superseded(root: Path | str) -> int:
    """One-time sweep: flip any decision named in a later row's Supersedes column but still
    marked `accepted` to `superseded`. Returns the number changed; idempotent (a second run
    changes nothing). Fixes the pre-BG0068 rows (e.g. D0012/D0013 in this repo)."""
    p = _log_path(Path(root))
    if not p.exists():
        return 0
    lines = p.read_text(encoding="utf-8").splitlines()
    targets: set[str] = set()
    for ln in lines:
        if not _ROW.match(ln):
            continue
        parts = _UNESCAPED_PIPE.split(ln)
        if len(parts) > _STATUS_CELL + 1:
            nid = _norm_did(parts[_STATUS_CELL + 1].strip())  # the Supersedes cell
            if nid:
                targets.add(nid)
    changed = sum(1 for t in targets if _flip_to_superseded(lines, t) == "changed")
    if changed:
        sdlc_md.atomic_write(p, "\n".join(lines) + "\n")
    return changed


def list_decisions(root: Path | str, status: str | None = None) -> list[dict]:
    p = _log_path(Path(root))
    if not p.exists():
        return []
    out = []
    for ln in p.read_text(encoding="utf-8").splitlines():
        if not _ROW.match(ln):
            continue
        # split on UNESCAPED pipes and unescape, so a `\|` inside a decision/rationale cell
        # does not fracture into extra columns and shift the Status/Supersedes fields
        cells = [c.strip().replace("\\|", "|")
                 for c in _UNESCAPED_PIPE.split(ln.strip().strip("|"))]
        if len(cells) >= 6:
            rec = {"id": cells[0], "decision": cells[1], "rationale": cells[2],
                   "status": cells[3], "supersedes": cells[4], "date": cells[5]}
            if status is None or rec["status"] == status:
                out.append(rec)
    return out


#: The prose a ruling is made of. Both fields are free text an author writes, so both belong in
#: the document rather than in a shell argument.
PROSE_KEYS: tuple[str, ...] = ("decision", "rationale")


def resolve_prose(args: argparse.Namespace, keys: tuple[str, ...] = PROSE_KEYS) -> dict:
    """The ruling's prose, from the `--fields-file` document or the flags, through the ONE
    shared loader. Raises ValueError when a required field is in neither."""
    import file_finding  # noqa: PLC0415 - the shared prose-fields loader, as elsewhere
    fields = file_finding.resolve_prose_fields(
        getattr(args, "fields_file", None),
        {k: getattr(args, k, None) for k in keys}, allowed=keys)
    missing = [k for k in keys if not str(fields.get(k) or "").strip()]
    if missing:
        raise ValueError(f"no {'/'.join(missing)} - pass --{missing[0]}, or a "
                         f"\"{missing[0]}\" key in the --fields-file document")
    return fields


def add_fields_file_arg(sp: argparse.ArgumentParser, keys: tuple[str, ...]) -> None:
    """Declare the non-shell input path on a subparser, spelled the same way everywhere."""
    sp.add_argument("--fields-file", dest="fields_file", metavar="FIELDS.json",
                    help="read the ruling from a JSON object ({\"" + keys[0] + "\": \"...\"}) "
                         "instead of the flags, so prose carrying shell metacharacters is "
                         "stored verbatim rather than interpreted by the shell; `-` reads the "
                         "document from stdin")


def cmd_add(args: argparse.Namespace) -> int:
    try:
        fields = resolve_prose(args)
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    r = add(args.root, fields["decision"], fields["rationale"], args.status,
            args.supersedes or "")
    print(json.dumps(r, indent=2) if args.format == "json"
          else f"recorded {r['id']} ({r['status']}) on {r['date']}")
    return 0


def cmd_promote(args: argparse.Namespace) -> int:
    try:
        fields = resolve_prose(args)
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    r = promote(args.root, args.source, fields["decision"], fields["rationale"])
    print(json.dumps(r, indent=2) if args.format == "json"
          else f"promoted {args.source} -> {r['id']} ({r['date']})")
    return 0


def cmd_backfill(args: argparse.Namespace) -> int:
    n = backfill_superseded(args.root)
    print(f"backfilled {n} stale-accepted row(s) to superseded")
    return 0


def cmd_waive(args: argparse.Namespace) -> int:
    subject = f"leg:{args.leg}" if args.leg else args.subject
    try:
        fields = resolve_prose(args, ("rationale",))
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    try:
        r = record_waiver(args.root, subject, fields["rationale"],
                          authorised_by=getattr(args, "authorised_by", "") or "")
    except ValueError as exc:
        print(f"waive refused: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(r, indent=2) if args.format == "json"
          else f"waived {_norm_subject(subject)} -> {r['id']} ({r['date']})")
    return 0


def cmd_list(args: argparse.Namespace) -> int:
    rows = list_decisions(args.root, args.status)
    if args.format == "json":
        print(json.dumps(rows, indent=2))
        return 0
    if not rows:
        print("no decisions recorded")
        return 0
    for r in rows:
        print(f"{r['id']} [{r['status']}] {r['decision']} - {r['rationale']} ({r['date']})")
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Project decisions log.")
    sub = p.add_subparsers(dest="cmd", required=True)
    a = sub.add_parser("add", help="Append a decision (auto-numbered, dated).")
    a.add_argument("--decision", help="required unless the --fields-file document carries one")
    a.add_argument("--rationale", help="required unless the --fields-file document carries one")
    add_fields_file_arg(a, PROSE_KEYS)
    a.add_argument("--status", default="accepted", choices=("accepted", "superseded", "revisited"))
    a.add_argument("--supersedes", default="", help="the D-id this replaces, if any")
    a.add_argument("--root", default=".")
    a.add_argument("--format", choices=("text", "json"), default="text")
    a.set_defaults(func=cmd_add)
    bf = sub.add_parser("backfill", help="Flip rows superseded-in-lineage but still marked accepted.")
    bf.add_argument("--root", default=".")
    bf.add_argument("--format", choices=("text", "json"), default="text")
    bf.set_defaults(func=cmd_backfill)
    pr = sub.add_parser("promote", help="Promote a resolved PRD open question into the log (back-linked).")
    pr.add_argument("--from", dest="source", required=True, help="the PRD open-question id, e.g. PRD-OQ3")
    pr.add_argument("--decision", help="required unless the --fields-file document carries one")
    pr.add_argument("--rationale", help="required unless the --fields-file document carries one")
    add_fields_file_arg(pr, PROSE_KEYS)
    pr.add_argument("--root", default=".")
    pr.add_argument("--format", choices=("text", "json"), default="text")
    pr.set_defaults(func=cmd_promote)
    wv = sub.add_parser("waive", help="Record a waiver: a required leg or rule is intentionally "
                                      "out of scope here (a machine-detectable decision row).")
    wv_what = wv.add_mutually_exclusive_group(required=True)
    wv_what.add_argument("--leg", choices=DOC_LEGS,
                         help="the required document leg being waived (CODE is out of scope)")
    wv_what.add_argument("--subject", help="a general waiver subject, e.g. rule:engagement-floor "
                                           "or rule:conformance:critiqued:US0103-US0310 (the "
                                           "rule must be one a checker declares, and an optional "
                                           "`:<unit>`/`:<id>-<id>` tail scopes it)")
    wv.add_argument("--rationale", help="why it is out of scope for this project (required "
                                        "unless the --fields-file document carries one)")
    add_fields_file_arg(wv, ("rationale",))
    wv.add_argument("--root", default=".")
    wv.add_argument("--format", choices=("text", "json"), default="text")
    wv.add_argument("--authorised-by", dest="authorised_by", default="", metavar="WHO",
                    help="who authorised setting the rule aside. Required for a "
                         "rule:sprint-checklist waiver: a compulsory close item set aside by "
                         "nobody in particular is a decision with no decider")
    wv.set_defaults(func=cmd_waive)
    ls = sub.add_parser("list", help="List recorded decisions.")
    ls.add_argument("--status", help="filter by status")
    ls.add_argument("--root", default=".")
    ls.add_argument("--format", choices=("text", "json"), default="text")
    ls.set_defaults(func=cmd_list)
    sdlc_md.add_global_root(p)
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    # Resolve the root ONCE and write it back, so every verb below anchors on the tree the
    # run belongs to. The family default `.` means "work it out from here", not "the cwd
    # is the project": otherwise a run from a subdirectory acts on a stray tree and exits 0.
    args.root = str(sdlc_md.resolve_root(args))
    return args.func(args)


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        sys.exit(130)
    except Exception as exc:  # noqa: BLE001
        print(f"error: {exc}", file=sys.stderr)
        sys.exit(1)
