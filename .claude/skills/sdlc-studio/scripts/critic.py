#!/usr/bin/env python3
"""SDLC Studio critic-verdict record (CR0023).

The independent non-author critic (RFC0001 D3) judges each unit's diff against the
AC intent. Its verdict used to be ephemeral, so nothing could confirm the critic
actually ran. Here it is a committed, append-only record
(`sdlc-studio/reviews/critic-verdicts.md`), so the conformance gate can require it:
"the critic ran" becomes a deterministic, auditable signal - the cheap part of
RFC0001's deferred Stop-Hook, with no harness dependency. Pure stdlib.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lib import sdlc_md  # noqa: E402

APPROVE, REJECT = "APPROVE", "REJECT"
HEADER = (
    "# Critic Verdicts\n\n"
    "> Append-only. The independent non-author critic's verdict per unit (RFC0001 D3).\n"
    "> APPROVE = ready; REJECT = repair before Done. Latest row per unit wins.\n\n"
    "| Unit | Verdict | Reviewer | Date | Issues |\n| --- | --- | --- | --- | --- |\n"
)


def verdicts_path(repo_root: Path | str) -> Path:
    return Path(repo_root) / "sdlc-studio" / "reviews" / "critic-verdicts.md"


def _clean(value: str) -> str:
    return value.replace("|", "/").replace("\n", " ").strip()


def record_verdict(repo_root: Path | str, unit: str, verdict: str,
                   reviewer: str = "independent-critic", issues: str = "") -> Path:
    """Append a critic verdict for a unit (creating the table if absent)."""
    path = verdicts_path(repo_root)
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists():
        path.write_text(HEADER, encoding="utf-8")
    row = (f"| {sdlc_md.norm_id(unit)} | {verdict.upper()} | {_clean(reviewer)} | "
           f"{sdlc_md.now_date()} | {_clean(issues) or '-'} |\n")
    with path.open("a", encoding="utf-8") as fh:  # append-only
        fh.write(row)
    return path


def read_verdicts(repo_root: Path | str) -> list[dict]:
    """All recorded verdicts in order, as {unit, verdict, reviewer, date, issues}."""
    path = verdicts_path(repo_root)
    if not path.exists():
        return []
    out: list[dict] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.startswith("|"):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) != 5 or cells[0] == "Unit" or set(cells[0]) <= {"-"}:
            continue
        out.append(dict(zip(("unit", "verdict", "reviewer", "date", "issues"), cells)))
    return out


def verdict_for(repo_root: Path | str, unit: str):
    """The latest recorded verdict for a unit, or None."""
    target = sdlc_md.norm_id(unit)
    latest = None
    for v in read_verdicts(repo_root):
        if sdlc_md.norm_id(v["unit"]) == target:
            latest = v
    return latest


def cmd_record(args: argparse.Namespace) -> int:
    path = record_verdict(args.root, args.unit, args.verdict, args.reviewer, args.issues)
    print(f"recorded {sdlc_md.norm_id(args.unit)} {args.verdict.upper()} -> {path}")
    return 0


def cmd_show(args: argparse.Namespace) -> int:
    if args.unit:
        v = verdict_for(args.root, args.unit)
        print(v if v else f"no verdict for {args.unit}")
    else:
        for v in read_verdicts(args.root):
            print(f"{v['unit']} {v['verdict']} ({v['date']})")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="SDLC Studio critic-verdict record.")
    sub = parser.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("record", help="Record a critic verdict for a unit.")
    r.add_argument("--unit", required=True)
    r.add_argument("--verdict", required=True, choices=("approve", "reject", "APPROVE", "REJECT"))
    r.add_argument("--reviewer", default="independent-critic")
    r.add_argument("--issues", default="")
    r.add_argument("--root", default=".")
    r.set_defaults(func=cmd_record)
    s = sub.add_parser("show", help="Show the latest verdict for a unit (or all).")
    s.add_argument("--unit", default=None)
    s.add_argument("--root", default=".")
    s.set_defaults(func=cmd_show)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
