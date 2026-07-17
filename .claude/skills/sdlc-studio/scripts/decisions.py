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
import json
import re
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lib import sdlc_md  # noqa: E402

SKILL = Path(__file__).resolve().parent.parent
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


def record_waiver(root: Path | str, subject: str, rationale: str,
                  today: str | None = None) -> dict:
    """Record a machine-detectable waiver: a decision row `waiver: <subject>`, with the human
    reason in the rationale cell. General over any waivable subject (a review leg `leg:tsd`, or
    a rule `rule:engagement-floor`), so a later gate reuses the same primitive."""
    subject = _norm_subject(subject)
    if not subject:
        raise ValueError("a waiver subject must be non-empty (e.g. leg:tsd or rule:<name>)")
    return add(root, f"{WAIVER_PREFIX} {subject}", rationale, today=today)


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


def cmd_add(args: argparse.Namespace) -> int:
    r = add(args.root, args.decision, args.rationale, args.status, args.supersedes or "")
    print(json.dumps(r, indent=2) if args.format == "json"
          else f"recorded {r['id']} ({r['status']}) on {r['date']}")
    return 0


def cmd_promote(args: argparse.Namespace) -> int:
    r = promote(args.root, args.source, args.decision, args.rationale)
    print(json.dumps(r, indent=2) if args.format == "json"
          else f"promoted {args.source} -> {r['id']} ({r['date']})")
    return 0


def cmd_backfill(args: argparse.Namespace) -> int:
    n = backfill_superseded(args.root)
    print(f"backfilled {n} stale-accepted row(s) to superseded")
    return 0


def cmd_waive(args: argparse.Namespace) -> int:
    subject = f"leg:{args.leg}" if args.leg else args.subject
    r = record_waiver(args.root, subject, args.rationale)
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
    a.add_argument("--decision", required=True)
    a.add_argument("--rationale", required=True)
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
    pr.add_argument("--decision", required=True)
    pr.add_argument("--rationale", required=True)
    pr.add_argument("--root", default=".")
    pr.add_argument("--format", choices=("text", "json"), default="text")
    pr.set_defaults(func=cmd_promote)
    wv = sub.add_parser("waive", help="Record a waiver: a required leg or rule is intentionally "
                                      "out of scope here (a machine-detectable decision row).")
    wv_what = wv.add_mutually_exclusive_group(required=True)
    wv_what.add_argument("--leg", choices=DOC_LEGS,
                         help="the required document leg being waived (CODE is out of scope)")
    wv_what.add_argument("--subject", help="a general waiver subject, e.g. rule:engagement-floor")
    wv.add_argument("--rationale", required=True, help="why it is out of scope for this project")
    wv.add_argument("--root", default=".")
    wv.add_argument("--format", choices=("text", "json"), default="text")
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
    return args.func(args)


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        sys.exit(130)
    except Exception as exc:  # noqa: BLE001
        print(f"error: {exc}", file=sys.stderr)
        sys.exit(1)
