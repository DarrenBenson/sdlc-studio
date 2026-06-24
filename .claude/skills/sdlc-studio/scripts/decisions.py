#!/usr/bin/env python3
"""Project decisions log - the canonical home for load-bearing decisions (CR0080).

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

SKILL = Path(__file__).resolve().parent.parent
LOG_REL = "sdlc-studio/decisions.md"
_ROW = re.compile(r"^\|\s*D(\d{4})\s*\|")


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
    p.write_text(text, encoding="utf-8")
    return True


def _next_id(text: str) -> str:
    nums = [int(m.group(1)) for m in (_ROW.match(ln) for ln in text.splitlines()) if m]
    return f"D{(max(nums) + 1) if nums else 1:04d}"


def add(root: Path | str, decision: str, rationale: str, status: str = "accepted",
        supersedes: str = "", today: str | None = None) -> dict:
    root = Path(root)
    ensure_log(root)
    p = _log_path(root)
    lines = p.read_text(encoding="utf-8").splitlines()
    did = _next_id("\n".join(lines))
    when = today or date.today().isoformat()
    cells = [did, decision.replace("|", "\\|"), rationale.replace("|", "\\|"),
             status, supersedes or "--", when]
    row = "| " + " | ".join(cells) + " |"
    # insert after the data-table header+separator (the row carrying the ID column)
    hdr = next((i for i, ln in enumerate(lines)
                if ln.strip().startswith("| ID |") or ln.strip().startswith("| ID|")), None)
    if hdr is None:
        raise ValueError("decisions.md has no decisions table")
    last = max((i for i in range(hdr + 2, len(lines)) if _ROW.match(lines[i])), default=hdr + 1)
    lines.insert(last + 1, row)
    p.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return {"id": did, "status": status, "date": when}


def promote(root: Path | str, source: str, decision: str, rationale: str,
            today: str | None = None) -> dict:
    """Promote a resolved PRD open question into the log with a back-link (CR0080). One
    record, two views: the question stays in `PRD §Open Questions`; this records the
    resolution here as `[from <source>]`, never duplicating it as free text in both."""
    return add(root, decision, f"{rationale} [from {source}]", today=today)


def list_decisions(root: Path | str, status: str | None = None) -> list[dict]:
    p = _log_path(Path(root))
    if not p.exists():
        return []
    out = []
    for ln in p.read_text(encoding="utf-8").splitlines():
        if not _ROW.match(ln):
            continue
        cells = [c.strip() for c in ln.strip().strip("|").split("|")]
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
    p = argparse.ArgumentParser(description="Project decisions log (CR0080).")
    sub = p.add_subparsers(dest="cmd", required=True)
    a = sub.add_parser("add", help="Append a decision (auto-numbered, dated).")
    a.add_argument("--decision", required=True)
    a.add_argument("--rationale", required=True)
    a.add_argument("--status", default="accepted", choices=("accepted", "superseded", "revisited"))
    a.add_argument("--supersedes", default="", help="the D-id this replaces, if any")
    a.add_argument("--root", default=".")
    a.add_argument("--format", choices=("text", "json"), default="text")
    a.set_defaults(func=cmd_add)
    pr = sub.add_parser("promote", help="Promote a resolved PRD open question into the log (back-linked).")
    pr.add_argument("--from", dest="source", required=True, help="the PRD open-question id, e.g. PRD-OQ3")
    pr.add_argument("--decision", required=True)
    pr.add_argument("--rationale", required=True)
    pr.add_argument("--root", default=".")
    pr.add_argument("--format", choices=("text", "json"), default="text")
    pr.set_defaults(func=cmd_promote)
    ls = sub.add_parser("list", help="List recorded decisions.")
    ls.add_argument("--status", help="filter by status")
    ls.add_argument("--root", default=".")
    ls.add_argument("--format", choices=("text", "json"), default="text")
    ls.set_defaults(func=cmd_list)
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
