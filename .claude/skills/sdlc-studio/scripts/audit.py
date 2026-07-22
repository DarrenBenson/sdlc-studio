#!/usr/bin/env python3
"""SDLC Studio tranche audit - sprint pre-flight readiness.

Runs between `sprint plan` and the triage STOP, so the operator approves a
clean, verifiable batch. Per unit it flags, deterministically:

- **weak-AC**       - no checkable AC, or the tautology placeholder (the
                      vacuous-pass class the downstream verify/conformance miss),
- **unmet-deps**    - a `Depends on` referent that is not yet delivered. Referents resolve
                      in-repo first, then across the sibling repos a PVD product manifest
                      names, so a cross-repo dependency delivered elsewhere counts as met,
- **unresolved-deps** - a referent the audit could not check at all because the manifest's
                      sibling checkout is not on disk (named, never silently passed),
- **already-terminal** - already Complete/Superseded/Done (close, do not re-work),
- **missing-regression-test** - a Fixed/Done bug whose recorded tests carry no
                      integration/regression-level case (name-signal only; the seam
                      judgement stays with review - see best-practices/testing.md),
- **link-integrity** - reuses `integrity.py`'s error findings for the unit.

Emits a JSON readiness report; exits non-zero when any unit is not ready. The
adversarial "is the problem still real" lens stays model-instructed (delegates to
the adversarial audit when built). Read-only; pure stdlib.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lib import conventions, sdlc_md, xrepo  # noqa: E402  (xrepo: cross-repo id resolution)
import integrity  # noqa: E402  (sibling script; scripts dir is on sys.path)
import sprint  # noqa: E402
import verify_ac  # noqa: E402  (reuse the Verify-line lint)
import ac_scope  # noqa: E402  (reuse the cross-epic AC check)

TAUTOLOGY = "lint and tests green"
# An unexpanded `{{...}}` span from the scaffolding template. A unit carrying one
# has AC-shaped markup but no authored criterion, so an item count alone reads it
# as groomed - and `verify_ac` would then run `{{executable check}}` as its oracle.
_PLACEHOLDER = re.compile(r"\{\{[^}]*\}\}")
# A dependency counts as met once it has been delivered (or replaced).
MET = {"Done", "Complete", "Verified", "Fixed", "Accepted", "Superseded", "Closed"}
# Terminal-but-not-delivered: the dependency is dead, surfaced distinctly.
DEAD = {"Rejected", "Withdrawn", "Won't Implement", "Won't Fix", "Deferred"}
_AC_CHECKBOX = re.compile(r"^\s*- \[[ xX]\] ")

# Every readiness issue kind audit_unit can put in a unit's `issues`, whose prefix
# (before any `: detail` suffix) is fed to sdlc_md.remediation_lines("audit", ...) by
# cmd_check. This is audit's finding-kind vocabulary and the single source of truth for
# it: the remediation registry (sdlc_md.REMEDIATION["audit"]) must carry a hint for each,
# a guard derives its expected key set from this tuple (so a new issue kind without a hint
# reddens the guard), and a sibling test asserts this tuple matches the kinds actually
# appended in source (so the tuple itself cannot silently drift). Informational `info`
# notes (e.g. sequenced-in-batch) never block readiness and are not remediation kinds.
# Keep this in step with the issue literals in audit_unit below.
FINDING_KINDS = (
    "not-found",
    "weak-AC",
    "weak-verify",
    "underspecified",
    "missing-regression-test",
    "cross-epic-ac",
    "unmet-deps",
    "unresolved-deps",
    "already-terminal",
    "link-integrity",
    "already-satisfied",
)


# --------------------------------------------------------------------------
# Lens profiles
# --------------------------------------------------------------------------
# A profile is a declarative lens pack: a name, an adversarial question and what the
# lens hunts, one row per lens. Packs ship under templates/audit-profiles/; the default
# project profile is declared in the reference instead, so both are resolved here and a
# name no profile declares is refused rather than silently running zero lenses.
SKILL_DIR = Path(__file__).resolve().parent.parent
PROFILE_DIR = SKILL_DIR / "templates" / "audit-profiles"
#: Profiles declared in a reference section rather than as a pack file, mapped to the
#: file and the heading anchor whose section holds the lens table.
REFERENCE_PROFILES = {"project": ("reference-audit.md", "audit-project-profile")}
_REFUTE_RE = re.compile(r"\*\*Refute panel:\*\*(.*)", re.I)
_THRESHOLD_RE = re.compile(r">=\s*(\d+)\s*of\s*(\d+)")
_TABLE_DIVIDER_RE = re.compile(r"^\|[\s:|-]+\|$")


class UnknownProfile(ValueError):
    """A profile name no pack and no reference section declares."""


def profile_names(skill_dir: Path | None = None) -> list[str]:
    """Every profile that can be resolved, sorted. Packs on disk plus the
    reference-declared defaults."""
    # PROFILE_DIR is the one answer to "where do the packs live". This used to recompute
    # the same path inline, leaving the constant defined and unused - dead, and therefore
    # unpinnable by any test.
    d = (skill_dir / "templates" / "audit-profiles") if skill_dir else PROFILE_DIR
    packs = {p.stem for p in d.glob("*.md")} if d.is_dir() else set()
    return sorted(packs | set(REFERENCE_PROFILES))


def _split_row(line: str) -> list[str]:
    return [c.strip() for c in line.strip().strip("|").split("|")]


def _parse_lens_table(lines: list[str]) -> tuple[list[str], list[dict]]:
    """(column headers, lens rows) for the first markdown table in `lines`.

    A lens row is `{name, question, hunts, drawn_from}`. Every cell after the first is
    filled when the row has it and left empty otherwise, never dropped: a two-column
    table (the project profile's artifact/lens shape) yields an empty `hunts`, and a
    pack with no provenance column an empty `drawn_from`. `drawn_from` carries the
    recorded failure modes a lens was drawn from, as lesson ids, for the packs that
    cite them. Nothing here judges a row's content; a pack that must declare more is
    held to it by its own test.
    """
    columns: list[str] = []
    lenses: list[dict] = []
    header: list[str] | None = None
    for line in lines:
        stripped = line.strip()
        if not stripped.startswith("|"):
            if header is not None and columns:
                break  # the table ended; ignore any later table in the file
            continue
        cells = _split_row(stripped)
        if header is None:
            header = cells
            continue
        if _TABLE_DIVIDER_RE.match(stripped):
            columns = header
            continue
        if not columns:  # a table without a divider row is not a lens table
            continue
        lenses.append({"name": cells[0],
                       "question": cells[1] if len(cells) > 1 else "",
                       "hunts": cells[2] if len(cells) > 2 else "",
                       "drawn_from": cells[3] if len(cells) > 3 else ""})
    return columns, lenses


def _refute_declaration(text: str) -> str:
    """The whole `**Refute panel:**` blockquote, joined. Taken as a block rather than a
    single line so a declaration wrapped across lines is read in full."""
    lines = text.splitlines()
    for i, line in enumerate(lines):
        if _REFUTE_RE.search(line):
            block = [line]
            for nxt in lines[i + 1:]:
                if not nxt.lstrip().startswith(">"):
                    break
                block.append(nxt)
            joined = " ".join(part.lstrip().lstrip(">").strip() for part in block)
            return _REFUTE_RE.search(joined).group(1).strip()
    return ""


def _parse_threshold(text: str) -> dict | None:
    """The refute threshold a `**Refute panel:**` declaration states, as
    `{survive, votes}`. None when the declaration is absent or states no threshold."""
    m = _THRESHOLD_RE.search(_refute_declaration(text))
    if not m:
        return None
    return {"survive": int(m.group(1)), "votes": int(m.group(2))}


def parse_pack(path: Path | str) -> dict:
    """Parse a lens pack file into `{columns, lenses, refute, threshold}`."""
    text = Path(path).read_text(encoding="utf-8")
    columns, lenses = _parse_lens_table(text.splitlines())
    return {"columns": columns, "lenses": lenses,
            "refute": _refute_declaration(text),
            "threshold": _parse_threshold(text)}


def _reference_section(skill_dir: Path, filename: str, anchor: str) -> str:
    """The body of the heading whose anchor is `{#anchor}`, up to the next heading of
    the same or a higher level."""
    text = (skill_dir / filename).read_text(encoding="utf-8")
    lines = text.splitlines()
    start = level = None
    for i, line in enumerate(lines):
        if line.startswith("#") and f"{{#{anchor}}}" in line:
            start = i + 1
            level = len(line) - len(line.lstrip("#"))
            break
    if start is None:
        return ""
    out: list[str] = []
    for line in lines[start:]:
        if line.startswith("#"):
            if len(line) - len(line.lstrip("#")) <= level:
                break
        out.append(line)
    return "\n".join(out)


def resolve_profile(name: str, skill_dir: Path | None = None) -> dict:
    """Resolve a profile name to its lens pack.

    Returns `{name, source, lenses, refute, threshold, columns}`. Raises
    `UnknownProfile` for a name nothing declares, and for a declaration that
    carries no lens at all - an empty lens set is a broken profile, never a run.
    """
    d = skill_dir or SKILL_DIR
    known = profile_names(d)
    pack = d / "templates" / "audit-profiles" / f"{name}.md"
    if pack.is_file():
        parsed = parse_pack(pack)
        source = f"templates/audit-profiles/{name}.md"
    elif name in REFERENCE_PROFILES:
        filename, anchor = REFERENCE_PROFILES[name]
        body = _reference_section(d, filename, anchor)
        columns, lenses = _parse_lens_table(body.splitlines())
        parsed = {"columns": columns, "lenses": lenses,
                  "refute": _refute_declaration(body),
                  "threshold": _parse_threshold(body)}
        source = f"{filename}#{anchor}"
    else:
        raise UnknownProfile(
            f"unknown audit profile {name!r}; profiles that exist: {', '.join(known)}")
    if not parsed["lenses"]:
        raise UnknownProfile(f"audit profile {name!r} declares no lens ({source})")
    return {"name": name, "source": source, **parsed}


def cmd_profile(args: argparse.Namespace) -> int:
    """Resolve a profile and report its lenses plus the refute threshold."""
    if args.list or not args.name:
        names = profile_names()
        if args.format == "json":
            print(json.dumps({"profiles": names}, indent=2))
        else:
            print("audit profiles: " + ", ".join(names))
        return 0
    try:
        p = resolve_profile(args.name)
    except UnknownProfile as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    if args.format == "json":
        print(json.dumps(p, indent=2))
        return 0
    print(f"profile {p['name']} -> {p['source']}")
    print(f"lenses: {len(p['lenses'])}")
    for lens in p["lenses"]:
        print(f"  {lens['name']}: {lens['question']}")
    t = p["threshold"]
    print(f"refute panel: {t['survive']} of {t['votes']} votes" if t
          else "refute panel: NOT DECLARED (the pack must state its threshold)")
    return 0


def find_artifact(root: Path, rec_id: str):
    """Locate an artifact file by id across all types; return (path, type) or None.
    Delegates to the shared `sdlc_md.find_by_id` (one source of truth, alias-aware)."""
    return sdlc_md.find_by_id(root, rec_id)


def _weak_ac(text: str) -> bool:
    """True when the unit has no checkable AC, or the AC are not authored.

    Three ways an AC section fails to be a criterion anyone can check: it holds no
    AC-shaped item at all; an item is the tautology phrase; or the section still
    carries an unexpanded `{{...}}` span from the scaffolding template. The last is
    judged over the whole section rather than the collected items, because a
    criterion's `Verify:` line is part of it whether or not that line is itself
    counted as an item - and the Verify line is precisely what a downstream oracle
    would go on to execute.
    """
    items: list[str] = []
    section: list[str] = []
    in_ac = False
    for line in text.splitlines():
        if line.startswith("## "):
            in_ac = "acceptance criteria" in line.lower()
            continue
        if not in_ac:  # only AC inside the Acceptance Criteria section count
            continue
        section.append(line)
        if (_AC_CHECKBOX.match(line) or sdlc_md.AC_HEADING_RE.match(line)
                or sdlc_md.AC_BULLET_RE.match(line)):
            items.append(line)
    if not items:
        return True
    if any(_PLACEHOLDER.search(line) for line in section):
        return True
    return any(TAUTOLOGY in i.lower() for i in items)


def _bug_underspecified(text: str, root: Path | None = None) -> bool:
    """A bug is ready when it documents how to reproduce AND a proposed fix.

    Bugs have no Acceptance Criteria section - judging them by `_weak_ac` would
    always flag them. Readiness for a bug is repro + fix presence instead.
    The accepted heading vocabularies live in the convention layer
    (`conventions.bug_ready_sections` declares a house set): the skill and
    template-revision names plus semantic equivalents - Symptom + Root cause
    counts as repro evidence, and 'Fix (proposed)' equals 'Proposed Fix'.
    """
    has_repro = conventions.section_present(text, "repro", root)
    has_fix = conventions.section_present(text, "fix", root)
    return not (has_repro and has_fix)


def _unmet_deps(root: Path, text: str) -> tuple[list[str], list[str]]:
    """(unmet, unresolved) referents of `Depends on`.

    Resolution runs through the shared `xrepo` helper, so a multi-repo product's real edge is
    seen: a referent delivered in another repo of the PVD manifest MEETS the dependency
    instead of being reported unmet. The two lists are distinct claims, never collapsed -
    `unmet` says the referent exists and is not delivered (or is dead), `unresolved` says the
    audit could not check it because the sibling checkout named in the manifest is not on
    disk. The second is reported with the repo and path named, so it can be neither a silent
    pass nor mistaken for a delivery failure.
    """
    val = sdlc_md.extract_field(text, "Depends on") or sdlc_md.extract_field(text, "Depends On")
    if not val or integrity._is_blank(val):
        return [], []
    repos = xrepo.manifest_repos(root)
    unmet: list[str] = []
    unresolved: list[str] = []
    for ref in sorted({sdlc_md.norm_id(r) for r in sdlc_md.ID_SEARCH_RE.findall(val)}):
        r = xrepo.resolve(ref, Path(root), repos)
        st = r["status"]
        if st is None:  # resolved nowhere: absent sibling checkout, or no such id at all
            if r["error"] == xrepo.MISSING:
                unmet.append(f"{ref}:missing")
            else:
                unresolved.append(f"{ref}: {r['error']}")
        elif st in DEAD:
            unmet.append(f"{ref}:{st}(dead)")
        elif st not in MET:
            unmet.append(f"{ref}:{st}")
    return unmet, unresolved


def _already_satisfied(root: Path, rid: str) -> bool:
    """True if the unit's executable ACs all pass in the verify-report: verified > 0,
    no failures, no stale. Such a Ready unit is already delivered (the audit cannot see a feature
    shipped under a different artifact, but a green verifier set is the deterministic signal) -
    surface it as a close-candidate, not work to build. Manual-only / AC-less units never match."""
    report = sdlc_md.read_json(root / "sdlc-studio" / ".local" / "verify-report.json", {})
    stories = report.get("stories", {})
    items = stories.items() if isinstance(stories, dict) else []
    for stem, e in items:
        if sdlc_md.norm_id(stem.split("-")[0]) == sdlc_md.norm_id(rid):
            return e.get("verified", 0) > 0 and not e.get("failed", 0) and not e.get("stale", 0)
    return False


def _weak_verify(text: str) -> bool:
    """True if a story has a non-executable / mis-written Verify line: reuses
    verify_ac.lint_verifier, so the breakdown flags prose-curl verifiers at design time instead
    of discovering them 0/7 at verify time."""
    for line in text.splitlines():
        m = verify_ac.VERIFY_RE.match(line)
        if m and verify_ac.lint_verifier(m.group(2).strip()):
            return True
    return False


_REGRESSION_RE = re.compile(r"regression|integration|\be2e\b|end[- ]to[- ]end", re.I)


def _missing_regression_test(text: str) -> bool:
    """CR0128 heuristic 2: a Fixed/Done bug should carry an integration- or regression-level test
    (the bug lived in the seams), not only a unit test on the root-cause file. This mechanises the
    NAME signal - a `Verify` line or a 'regression/integration/e2e' marker - and returns True for a
    bug that records tests but none at that level. It deliberately does NOT try to prove a test
    truly exercises the seams: that stays a review judgement (the advisory boundary recorded in
    CR0128). A bug with no test info at all is left to `underspecified`, not double-flagged here."""
    lines = text.splitlines()
    mentions_test = any("**verify:**" in low or "test" in low
                        for low in (line.lower() for line in lines))
    if not mentions_test:
        return False
    return not any(_REGRESSION_RE.search(line) for line in lines)


def audit_unit(root: Path | str, rec_id: str, integrity_errors: set[str] | None = None,
               cross_epic_ids: dict[str, dict] | None = None,
               batch_ids: set[str] | None = None) -> dict:
    """Readiness verdict for a single unit. A dependency that sits in the SAME batch
    (`batch_ids`) is the planner's dependency waves doing their job - reported as
    informational `sequenced-in-batch`, never `unmet-deps`."""
    root = Path(root)
    found = find_artifact(root, rec_id)
    if found is None:
        return {"id": sdlc_md.norm_id(rec_id), "status": "missing", "issues": ["not-found"], "ready": False}
    path, type_ = found
    text = path.read_text(encoding="utf-8")
    rid = sdlc_md.extract_record_id(path.stem) or path.stem
    status = sdlc_md.canonical_status(sdlc_md.extract_field(text, "Status"),
                                      sdlc_md.status_vocab(type_, root)) or "Unknown"
    issues: list[str] = []
    if type_ == "bug":
        if _bug_underspecified(text, root):
            issues.append("underspecified")
        if status in integrity.TERMINAL and _missing_regression_test(text):
            issues.append("missing-regression-test")
    elif _weak_ac(text):
        issues.append("weak-AC")
    if type_ == "story" and _weak_verify(text):  # non-executable Verify line
        issues.append("weak-verify")
    info: list[str] = []
    # Cross-epic AC leakage. `cross_epic_ids` maps a story id to its strongest hit; only a
    # MULTI-keyword hit blocks readiness. `ac_scope` is a single-word keyword heuristic that
    # documents itself as advisory, and every finding it produced against this repo was an
    # ordinary English word ("fixes", "residual", "cleanup", "around") shared with an
    # unrelated epic title. Blocking a tranche on that forced the author either to reword
    # innocent prose or to rescope an AC that was already correctly scoped.
    hit = (cross_epic_ids or {}).get(sdlc_md.norm_id(rid)) if cross_epic_ids else None
    if hit:
        if hit["advisory"]:
            info.append(f"cross-epic-ac (advisory, 1 shared keyword {hit['keyword']!r} with "
                        f"{hit['owner_epic']}) - a single common word is not evidence of scope leakage")
        else:
            issues.append("cross-epic-ac")
    unmet, unresolved = _unmet_deps(root, text)
    if unmet and batch_ids:
        # only a PENDING in-batch dep is the planner's sequencing at work; a dead
        # (Rejected/Superseded) or missing dep cannot be delivered by wave order.
        def _sequenceable(u: str) -> bool:
            return (sdlc_md.norm_id(u.split(":")[0]) in batch_ids
                    and not u.endswith(":missing") and "(dead)" not in u)
        sequenced = [u for u in unmet if _sequenceable(u)]
        unmet = [u for u in unmet if not _sequenceable(u)]
        info.extend(f"sequenced-in-batch: {u.split(':')[0]}" for u in sequenced)
    if unmet:
        issues.append("unmet-deps: " + ", ".join(unmet))
    if unresolved:  # the checkout is absent, so the dependency could not be checked either way
        issues.append("unresolved-deps: " + ", ".join(unresolved))
    if status in integrity.TERMINAL:
        issues.append("already-terminal")
    if integrity_errors and rid in integrity_errors:
        issues.append("link-integrity")
    if status not in integrity.TERMINAL and _already_satisfied(root, rid):
        issues.append("already-satisfied")  # verifiers pass -> close-candidate, don't build
    return {"id": rid, "type": type_, "status": status, "issues": issues,
            "info": info, "ready": not issues}


def audit_batch(repo_root: Path | str, ids: list[str]) -> dict:
    """Readiness report over a batch of unit ids."""
    root = Path(repo_root)
    ierr = {f["id"] for f in integrity.detect_integrity(root)["findings"] if f["severity"] == "error"}
    # cross-epic AC leakage, computed once for the batch (ac_scope is repo-wide)
    try:
        cross: dict[str, dict] = {}
        for f in ac_scope.check(root):
            if not f.get("story"):
                continue
            sid = sdlc_md.norm_id(f["story"])
            # Keep the STRONGEST hit per story: a blocking one must not be hidden behind an
            # advisory one that happened to sort first.
            if sid not in cross or f.get("strength", 1) > cross[sid].get("strength", 1):
                cross[sid] = f
    except Exception:  # noqa: BLE001 - advisory readiness check, never break the audit
        cross = {}
    batch_ids = {sdlc_md.norm_id(i) for i in ids}
    units = [audit_unit(root, i, ierr, cross, batch_ids=batch_ids) for i in ids]
    ready = sum(1 for u in units if u["ready"])
    return {
        "generated_at": sdlc_md.now_iso8601(),
        "units": units,
        "summary": {"total": len(units), "ready": ready, "not_ready": len(units) - ready},
    }


def cmd_check(args: argparse.Namespace) -> int:
    """Audit a batch (by ids or a status query); exit non-zero if any unit is not ready."""
    ids = sdlc_md.resolve_ids(args)
    query = args.crs if args.crs is not None else args.bugs if args.bugs is not None else args.stories
    if bool(ids) == (query is not None):
        print("specify exactly one selection mode: id(s) (--id/--ids) OR a status query "
              "(--crs/--bugs/--stories)", file=sys.stderr)
        return 2
    if not ids:
        kind, status = (("cr", args.crs) if args.crs is not None
                        else ("bug", args.bugs) if args.bugs is not None
                        else ("story", args.stories))
        ids = [b["id"] for b in sprint.select_batch(args.root, kind, status)]
    res = audit_batch(args.root, ids)
    if args.format == "json":
        print(json.dumps(res, indent=2))
    else:
        s = res["summary"]
        print(f"tranche audit: {s['ready']}/{s['total']} ready, {s['not_ready']} not")
        kinds = set()
        for u in res["units"]:
            if not u["ready"]:
                print(f"  NOT READY {u['id']} ({u['status']}): {'; '.join(u['issues'])}")
                kinds.update(i.split(":")[0].strip() for i in u["issues"])  # issue may carry a suffix
            for note in u.get("info", []):  # informational, never blocks readiness
                print(f"  note      {u['id']}: {note}")
        hints = sdlc_md.remediation_lines("audit", kinds)
        if hints:
            print("Guidance:")
            for h in hints:
                print(f"  - {h}")
    return 1 if res["summary"]["not_ready"] else 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="SDLC Studio tranche audit (sprint pre-flight).")
    sub = parser.add_subparsers(dest="cmd", required=True)
    c = sub.add_parser("check", help="Audit a batch for readiness before the triage STOP.")
    sdlc_md.add_ids_argument(c, help_="unit ids to audit; repeat --id or pass --ids as one "
                                      "comma list (e.g. --id CR0003 --id CR0004)")
    g = c.add_mutually_exclusive_group()
    g.add_argument("--crs", metavar="STATUS", help="CRs with this Status")
    g.add_argument("--bugs", metavar="STATUS", help="Bugs with this Status")
    g.add_argument("--stories", metavar="STATUS", help="Stories with this Status")
    c.add_argument("--root", default=".", help="Repo root (default: .)")
    c.add_argument("--format", choices=("text", "json"), default="text")
    c.set_defaults(func=cmd_check)
    p = sub.add_parser("profile", help="Resolve an audit lens profile (--name repo) or "
                                       "list the profiles that exist.")
    p.add_argument("--name", help="profile to resolve (e.g. repo, code, skill, project)")
    p.add_argument("--list", action="store_true", help="list the profiles that exist")
    p.add_argument("--format", choices=("text", "json"), default="text")
    p.set_defaults(func=cmd_profile)
    sdlc_md.add_global_root(parser)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
