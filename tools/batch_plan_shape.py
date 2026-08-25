"""Report units whose `## Test Plan` is not the shape `testplan derive` produces.

A plan row whose declared mutant cannot fail the test its own criterion names is decoration,
and `mutation.plan_execution` reports the criterion covered anyway: it joins on
`(criterion, row)` and never asks which node did the killing. An independent test-plan review
found SIX such rows across US0671, US0674 and US0676, over three rejection rounds, by reading
the ledger against the `Verify:` lines by hand (BG0606).

Three of the arrangements it found are visible without reading the ledger at all, because none
of them is what `testplan derive` would write:

- a criterion carrying TWO rows, one of which cannot fail its verifier
- a row filed under a criterion that does not make the claim the row pins
- a row FUSED into the previous row's Title cell, which a human reads and the parser cannot see

So this asks the cheap question - does `derive` report the unit UNCHANGED? - and names every
unit that answers no. It does not replace reading the ledger; it removes the three shapes that
never needed a ledger to detect.

Repo-only: not shipped with the skill. Pure stdlib.

    python3 tools/batch_plan_shape.py check US0671 US0674   # named units
    python3 tools/batch_plan_shape.py check --all           # every unit carrying a plan
"""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
VERIFY_AC = REPO / ".claude" / "skills" / "sdlc-studio" / "scripts" / "verify_ac.py"
ARTEFACT_DIRS = ("stories", "bugs")


def derive_report(unit: str, root: Path | None = None) -> tuple[bool, str]:
    """`(is_derived_shape, what the command said)` for one unit."""
    res = subprocess.run(
        [sys.executable, str(VERIFY_AC), "testplan", "derive", "--unit", unit, "--dry-run"],
        capture_output=True, text=True, cwd=str(root or REPO))
    out = (res.stdout + res.stderr).strip()
    return (res.returncode == 0 and "unchanged" in res.stdout), out


def units_with_a_plan(root: Path | None = None) -> list[str]:
    base = (root or REPO) / "sdlc-studio"
    found: list[str] = []
    for sub in ARTEFACT_DIRS:
        for path in sorted((base / sub).glob("*.md")):
            try:
                if "## Test Plan" in path.read_text(encoding="utf-8", errors="replace"):
                    found.append(path.name.split("-")[0])
            except OSError:
                continue
    return found


def check(units: list[str], root: Path | None = None) -> list[dict]:
    return [{"unit": u, "detail": why}
            for u in units for ok, why in [derive_report(u, root)] if not ok]


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    c = sub.add_parser("check")
    c.add_argument("units", nargs="*")
    c.add_argument("--all", action="store_true",
                   help="every unit carrying a `## Test Plan`")
    args = ap.parse_args(argv)
    units = units_with_a_plan() if args.all else args.units
    if not units:
        print("batch-plan-shape: no unit named and --all not given", file=sys.stderr)
        return 2
    faults = check(units)
    for f in faults:
        print(f"batch-plan-shape: {f['unit']} is not the shape `testplan derive` writes - "
              f"{f['detail']}", file=sys.stderr)
    print(f"batch-plan-shape: {len(units)} unit(s) checked, {len(faults)} off-shape")
    return 1 if faults else 0


if __name__ == "__main__":
    raise SystemExit(main())
