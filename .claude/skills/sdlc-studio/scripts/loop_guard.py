#!/usr/bin/env python3
"""SDLC Studio loop guardrails.

The three judgements the loop-engineering consensus says the model must not own,
as deterministic mechanisms:

- iteration cap        - N failed green attempts on a unit before it quarantines,
- repetition-breaker   - the same failure signature R times quarantines early,
- completion oracle    - the batch is done only when every unit is terminal.

Quarantine = mark the unit Blocked and continue (D2): never thrash, never silently
drop. The pure functions take a state dict so they are trivially testable; the CLI
persists state to `sdlc-studio/.local/loop-state.json` (run-local, like
`project-state.json`) and exits 3 on quarantine so a harness cannot miss it.
Pure stdlib.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lib import sdlc_md  # noqa: E402

TERMINAL = {"Done", "Blocked"}
QUARANTINE_EXIT = 3


def record_attempt(state: dict, unit: str, signature: str) -> dict:
    """Record one failed attempt on a unit; returns the updated state."""
    units = state.setdefault("units", {})
    u = units.setdefault(unit, {"attempts": 0, "signatures": []})
    u["attempts"] += 1
    u["signatures"].append(signature)
    return state


def verdict(state: dict, unit: str, cap: int = 3, repeat: int = 2) -> dict:
    """Decide whether a unit must quarantine.

    Returns {unit, attempts, quarantine, reason}. The cap fires when attempts reach
    `cap`; the repetition-breaker fires when one signature recurs `repeat` times
    while still under the cap.
    """
    u = state.get("units", {}).get(unit, {"attempts": 0, "signatures": []})
    attempts = u["attempts"]
    reason = ""
    if attempts >= cap:
        reason = "cap"
    else:
        sigs = u["signatures"]
        if any(sigs.count(s) >= repeat for s in set(sigs)):
            reason = "repeat"
    return {"unit": unit, "attempts": attempts, "quarantine": bool(reason), "reason": reason}


def is_complete(statuses: list[str]) -> bool:
    """The batch is complete only when every unit status is terminal (Done/Blocked)."""
    return all(s in TERMINAL for s in statuses)


def _state_path(args: argparse.Namespace) -> Path:
    if args.state:
        return Path(args.state)
    return Path(args.root) / "sdlc-studio" / ".local" / "loop-state.json"


def cmd_record(args: argparse.Namespace) -> int:
    """Record a failed attempt, persist state, exit 3 if the unit quarantines."""
    path = _state_path(args)
    path.parent.mkdir(parents=True, exist_ok=True)
    state = sdlc_md.read_json(path, {"units": {}})
    state = record_attempt(state, args.unit, args.signature)
    v = verdict(state, args.unit, cap=args.cap, repeat=args.repeat)
    path.write_text(json.dumps(state, indent=2), encoding="utf-8")
    if v["quarantine"]:
        print(f"{args.unit}: QUARANTINE after {v['attempts']} attempts (reason={v['reason']}) -> mark Blocked, continue")
        return QUARANTINE_EXIT
    print(f"{args.unit}: continue ({v['attempts']} attempt(s), under guardrails)")
    return 0


def cmd_status(args: argparse.Namespace) -> int:
    """Print the current guardrail verdict for a unit."""
    state = sdlc_md.read_json(_state_path(args), {"units": {}})
    v = verdict(state, args.unit, cap=args.cap, repeat=args.repeat)
    print(json.dumps(v, indent=2))
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="SDLC Studio loop guardrails.")
    sub = parser.add_subparsers(dest="cmd", required=True)
    for name, func, help_ in (
        ("record", cmd_record, "Record a failed attempt; exit 3 on quarantine."),
        ("status", cmd_status, "Show the guardrail verdict for a unit."),
    ):
        p = sub.add_parser(name, help=help_)
        p.add_argument("--unit", required=True, help="Unit id (e.g. US0010)")
        if name == "record":
            p.add_argument("--signature", required=True, help="Failure signature (e.g. test::name)")
        p.add_argument("--cap", type=int, default=3, help="Attempts before quarantine (default 3)")
        p.add_argument("--repeat", type=int, default=2, help="Same-signature repeats before quarantine (default 2)")
        p.add_argument("--state", default=None, help="State file (default <root>/sdlc-studio/.local/loop-state.json)")
        p.add_argument("--root", default=".", help="Repo root (default: .)")
        p.set_defaults(func=func)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
