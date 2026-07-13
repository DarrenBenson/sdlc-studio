#!/usr/bin/env python3
"""SDLC Studio loop guardrails.

The judgements the loop-engineering consensus says the model must not own, as
deterministic mechanisms:

- iteration cap        - N failed green attempts on a unit before it quarantines,
- repetition-breaker   - the same failure signature R times quarantines early,
- completion oracle    - the batch is done only when every unit is terminal,
- appetite breaker     - a declared wall-clock / unit-count ceiling on the whole run.

Quarantine = mark the unit Blocked and continue (D2): never thrash, never silently
drop. The pure functions take a state dict so they are trivially testable; the CLI
persists state to `sdlc-studio/.local/loop-state.json` (run-local, like
`project-state.json`) and exits 3 on quarantine so a harness cannot miss it.

The appetite breaker is a RUN-level ceiling, not a per-unit one: a declared appetite
(wall-clock minutes and/or a unit count) evaluated at unit BOUNDARIES, so a unit is
never abandoned mid-implementation. It reads elapsed from the run's `started_at` and
spends against units already terminal - both deterministic and harness-independent,
neither self-reported. Budget-exhausted is DISTINCT from quarantine: its own exit code
(4), and it touches nothing - the units are left in their true status, not Blocked. A
token number is never a gate here: a script cannot observe token spend, so it stays a
forecast reported by `sprint plan`, never read by this breaker. Pure stdlib.
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lib import run_state, sdlc_md  # noqa: E402
import config  # noqa: E402  (sibling - appetite.* project defaults)

TERMINAL = {"Done", "Blocked"}
QUARANTINE_EXIT = 3
BUDGET_EXIT = 4  # budget-exhausted: a CLEAN run stop, distinct from quarantine (3) - the
                 # harness must tell "spend is gone, units left as-is" from "this unit blocked".


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


def budget_verdict(appetite_minutes: float, appetite_units: int,
                   elapsed_minutes: float, units_done: int) -> dict:
    """Whether the run's declared appetite is spent, evaluated at a unit boundary.

    A ceiling of 0 (or falsey) on an axis is UNBOUNDED - that axis never fires, which is
    today's behaviour when no appetite is declared. Otherwise the axis fires the moment its
    spend reaches the ceiling (`>=`, so an exact-boundary spend stops the run - the whole
    point is not to start the unit that would overspend). Either axis alone is sufficient.

    Pure: elapsed and units are measured by the caller and passed in, so the rule is
    trivially testable and the mutation check (drop the `>=` and a test reddens) is direct.
    """
    reasons: list[str] = []
    if appetite_minutes and elapsed_minutes >= appetite_minutes:
        reasons.append("minutes")
    if appetite_units and units_done >= appetite_units:
        reasons.append("units")
    return {"exhausted": bool(reasons), "reason": "+".join(reasons),
            "elapsed_minutes": round(elapsed_minutes, 2), "units_done": units_done,
            "appetite_minutes": appetite_minutes, "appetite_units": appetite_units}


def elapsed_minutes(started_at: str | None, now: datetime | None = None) -> float:
    """Wall-clock minutes since the run opened. 0 when the run was never opened (no start
    time is fabricated - the breaker cannot fire on a run that does not exist). Clamped at 0
    so clock skew on a shared checkout cannot report a negative spend."""
    if not started_at:
        return 0.0
    try:
        start = datetime.strptime(started_at, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
    except (ValueError, TypeError):
        return 0.0
    now = now or datetime.now(timezone.utc)
    return max(0.0, (now - start).total_seconds() / 60.0)


def units_consumed(repo_root: Path | str, batch: list[str]) -> int:
    """How many of the run's approved units have reached a terminal status - the run's unit
    spend, READ FROM DISK, never self-reported. This is the completion oracle applied to the
    run's own batch, so the count the breaker gates on is the same fact the loop closes on."""
    root = Path(repo_root)
    done = 0
    for rid in batch or []:
        found = sdlc_md.find_by_id(root, rid)
        if not found:
            continue
        path, type_ = found
        try:
            text = path.read_text(encoding="utf-8")
        except OSError:
            continue
        status = sdlc_md.canonical_status(sdlc_md.extract_field(text, "Status"),
                                          sdlc_md.status_vocab(type_, root))
        if status in sdlc_md.terminal_statuses(type_):
            done += 1
    return done


def _resolve_appetite(root: Path, args: argparse.Namespace) -> tuple[float, int]:
    """The appetite in force, resolved most-specific-first: an explicit CLI flag, then the
    appetite the run declared at plan time (`run-state.json`), then the project default
    (`appetite.*` in config), then 0 (unbounded). A flag override lets an operator impose an
    ad-hoc ceiling on a run that opened without one - it is never auto-extension of a spent
    appetite, which is always a fresh run."""
    declared = run_state.read(root).get("appetite") or {}

    def pick(flag, key, default_key):
        if flag is not None:
            return flag
        if declared.get(key) is not None:
            return declared[key]
        return config.get(root, default_key, 0) or 0

    minutes = pick(args.appetite_minutes, "minutes", "appetite.minutes")
    units = pick(args.appetite_units, "units", "appetite.units")
    return float(minutes or 0), int(units or 0)


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
    sdlc_md.atomic_write(path, json.dumps(state, indent=2))  # atomic: a crash mid-write must not reset guardrail state
    if getattr(args, "format", "text") == "json":
        print(json.dumps(v, indent=2))
        return QUARANTINE_EXIT if v["quarantine"] else 0
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


def cmd_budget(args: argparse.Namespace) -> int:
    """Evaluate the run's appetite at a unit boundary; exit BUDGET_EXIT when it is spent.

    Read-only: unlike `record`, a spent budget marks NOTHING - the units keep their true
    status and the run stops cleanly. The loop calls this BETWEEN units, so the appetite is
    honoured at a boundary and no unit is abandoned mid-implementation."""
    root = Path(args.root)
    try:
        state = run_state.read(root)
    except run_state.RunStateError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    minutes, units = _resolve_appetite(root, args)
    elapsed = elapsed_minutes(state.get("started_at"))
    done = units_consumed(root, state.get("batch") or [])
    v = budget_verdict(minutes, units, elapsed, done)
    v["run_id"] = state.get("run_id")
    if getattr(args, "format", "text") == "json":
        print(json.dumps(v, indent=2))
        return BUDGET_EXIT if v["exhausted"] else 0
    if v["exhausted"]:
        print(f"appetite SPENT (reason={v['reason']}): {v['elapsed_minutes']} min elapsed"
              f"{f'/{minutes} budget' if minutes else ''}, {done} unit(s) done"
              f"{f'/{units} budget' if units else ''} -> stop cleanly, generate the handoff "
              f"(handoff generate --outcome budget-spent); units keep their true status")
        return BUDGET_EXIT
    if not minutes and not units:
        print(f"no appetite declared - run is unbounded ({v['elapsed_minutes']} min, "
              f"{done} unit(s) done)")
        return 0
    print(f"appetite OK: {v['elapsed_minutes']} min"
          f"{f'/{minutes}' if minutes else ''}, {done} unit(s) done"
          f"{f'/{units}' if units else ''} - continue")
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
            sdlc_md.add_format_arg(p)  # status is already JSON-only
        p.add_argument("--cap", type=int, default=3, help="Attempts before quarantine (default 3)")
        p.add_argument("--repeat", type=int, default=2, help="Same-signature repeats before quarantine (default 2)")
        p.add_argument("--state", default=None, help="State file (default <root>/sdlc-studio/.local/loop-state.json)")
        p.add_argument("--root", default=".", help="Repo root (default: .)")
        p.set_defaults(func=func)
    b = sub.add_parser("budget", help="Evaluate the run appetite at a unit boundary; "
                                      f"exit {BUDGET_EXIT} when it is spent.")
    b.add_argument("--appetite-minutes", type=float, default=None, dest="appetite_minutes",
                   help="wall-clock ceiling (minutes); overrides the declared/config appetite")
    b.add_argument("--appetite-units", type=int, default=None, dest="appetite_units",
                   help="unit-count ceiling; overrides the declared/config appetite")
    b.add_argument("--root", default=".", help="Repo root (default: .)")
    sdlc_md.add_format_arg(b)
    b.set_defaults(func=cmd_budget)
    sdlc_md.add_global_root(parser)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
