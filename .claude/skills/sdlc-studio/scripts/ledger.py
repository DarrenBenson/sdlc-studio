#!/usr/bin/env python3
"""SDLC Studio decisions ledger.

A committed, append-only per-tranche ledger under `sdlc-studio/decisions/`. Records
rulings (timestamp, decision, rationale) so an sprint run's decisions survive
context compaction and resume, instead of being re-litigated after a reset.
Append-only: opened in append mode, never read-modify-truncate (the footgun that
emptied US0006). Pure stdlib.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lib import sdlc_md  # noqa: E402

HEADER = (
    "# Decisions Ledger - {tranche}\n\n"
    "> Append-only. One row per ruling; earlier rulings are never rewritten.\n\n"
    "| At | Decision | Rationale |\n| --- | --- | --- |\n"
)


def ledger_path(repo_root: Path | str, tranche: str) -> Path:
    """The committed ledger file for a tranche."""
    return Path(repo_root) / "sdlc-studio" / "decisions" / f"{tranche}.md"


def _clean(cell: str) -> str:
    """Keep a value safe inside a one-line markdown table cell.

    Lossy by design: a literal `|` becomes `/` and newlines collapse to spaces, so
    a ruling can never corrupt the table or split into a dropped row. Faithful
    enough for a human-readable ledger.
    """
    return cell.replace("|", "/").replace("\n", " ").strip()


def append_decision(repo_root: Path | str, tranche: str, decision: str, rationale: str = "") -> Path:
    """Append a ruling to the tranche ledger, creating it (with header) if absent."""
    path = ledger_path(repo_root, tranche)
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists():
        path.write_text(HEADER.format(tranche=tranche), encoding="utf-8")
    row = f"| {sdlc_md.now_iso8601()} | {_clean(decision)} | {_clean(rationale)} |\n"
    with path.open("a", encoding="utf-8") as fh:  # append-only; never truncate
        fh.write(row)
    return path


def read_ledger(repo_root: Path | str, tranche: str) -> list[dict]:
    """Return the tranche's rulings as a list of {at, decision, rationale}."""
    path = ledger_path(repo_root, tranche)
    if not path.exists():
        return []
    rows: list[dict] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        cells = sdlc_md.table_cells(line)  # escaped-pipe-aware
        if not cells or len(cells) != 3:
            continue
        at, decision, rationale = cells
        if at == "At":  # header
            continue
        rows.append({"at": at, "decision": decision, "rationale": rationale})
    return rows


def cmd_record(args: argparse.Namespace) -> int:
    """Append a ruling and report where it landed."""
    path = append_decision(args.root, args.tranche, args.decision, args.rationale)
    print(f"recorded -> {path}")
    return 0


def cmd_show(args: argparse.Namespace) -> int:
    """Print the tranche ledger."""
    rows = read_ledger(args.root, args.tranche)
    if getattr(args, "format", "text") == "json":
        print(json.dumps({"tranche": args.tranche, "decisions": rows}, indent=2))
        return 0
    if not rows:
        print(f"no decisions for {args.tranche}")
        return 0
    for r in rows:
        print(f"{r['at']}  {r['decision']} - {r['rationale']}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="SDLC Studio decisions ledger.")
    sub = parser.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("record", help="Append a ruling to the tranche ledger.")
    r.add_argument("--tranche", "--unit", dest="tranche", required=True,
                   help="Tranche/unit id (e.g. CR0020); --unit is the family-standard alias")
    r.add_argument("--decision", required=True)
    r.add_argument("--rationale", default="")
    r.add_argument("--root", default=".", help="Repo root (default: .)")
    r.set_defaults(func=cmd_record)
    s = sub.add_parser("show", help="Print the tranche ledger.")
    s.add_argument("--tranche", "--unit", dest="tranche", required=True)
    s.add_argument("--root", default=".", help="Repo root (default: .)")
    sdlc_md.add_format_arg(s)
    s.set_defaults(func=cmd_show)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
