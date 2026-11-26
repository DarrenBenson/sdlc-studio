#!/usr/bin/env python3
"""SDLC Studio loop guardrails.

The judgements the loop-engineering consensus says the model must not own, as
deterministic mechanisms:

- iteration cap        - N failed green attempts on a unit before it quarantines,
- repetition-breaker   - the same failure signature R times quarantines early,
- completion oracle    - the batch is done only when every unit is terminal,
- appetite breaker     - a declared wall-clock / unit-count / spend ceiling on the whole run.

Quarantine = mark the unit Blocked and continue (D2): never thrash, never silently
drop. The pure functions take a state dict so they are trivially testable; the CLI
persists state to `sdlc-studio/.local/loop-state.json` (run-local, like
`project-state.json`) and exits 3 on quarantine so a harness cannot miss it.

The appetite breaker is a RUN-level ceiling, not a per-unit one: a declared appetite
(wall-clock minutes, a unit count and a spend, each optional) evaluated at unit BOUNDARIES,
so a unit is never abandoned mid-implementation. It reads elapsed from the run's `started_at`
and spends against units already terminal - both deterministic and harness-independent,
neither self-reported. Budget-exhausted is DISTINCT from quarantine: its own exit code
(4), and it touches nothing - the units are left in their true status, not Blocked.

Spend is the run's priced input-equivalent tokens, read from the session meter as a first
close reads it (`run_state.spend_now`), and only when a spend appetite is declared. The
total is transcript-measured but a LOWER BOUND, because delegated and sidechain spend is
supplied rather than observed, so the spend axis can fire late but never early. It warns at
`SPEND_WARNINGS` per cent; a meter that cannot read leaves the axis unjudged at that boundary
and says why, while minutes and units still judge. Pure stdlib.
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
# The family root resolver, not a second path-joining idiom: `resolve_root` honours a root
# the caller NAMED and discovers upward from the family default `.`, `under_root` anchors a
# relative path on the result. Reached through the module, per the monkeypatch rule.
import verify_ac  # noqa: E402  (sibling)

TERMINAL = {"Done", "Blocked"}
QUARANTINE_EXIT = 3
BUDGET_EXIT = 4  # budget-exhausted: a CLEAN run stop, distinct from quarantine (3) - the
                 # harness must tell "spend is gone, units left as-is" from "this unit blocked".
SPEND_WARNINGS = (95, 75)  # the per-cent shares of the spend appetite that warn, highest first


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
                   elapsed_minutes: float, units_done: int, *, appetite_spend: int = 0,
                   spend: int | None = None, spend_unread: str | None = None,
                   spend_includes_subagents: bool | None = None) -> dict:
    """Whether the run's declared appetite is spent, evaluated at a unit boundary.

    A ceiling of 0 (or falsey) on an axis is UNBOUNDED - that axis never fires, which is
    today's behaviour when no appetite is declared. Otherwise the axis fires the moment its
    spend reaches the ceiling (`>=`, so an exact-boundary spend stops the run - the whole
    point is not to start the unit that would overspend). Any axis alone is sufficient.

    The spend axis judges only a `spend` that was read: None, with `spend_unread` saying why,
    fires nothing and warns nothing. `spend_warning` is the highest of `SPEND_WARNINGS` the
    spend has reached, compared exactly in integers, or None.

    Pure: elapsed, units and spend are measured by the caller and passed in, so the rule is
    trivially testable and the mutation check (drop the `>=` and a test reddens) is direct.
    """
    reasons: list[str] = []
    if appetite_minutes and elapsed_minutes >= appetite_minutes:
        reasons.append("minutes")
    if appetite_units and units_done >= appetite_units:
        reasons.append("units")
    read = bool(appetite_spend) and isinstance(spend, int)
    if read and spend >= appetite_spend:
        reasons.append("spend")
    warning = next((band for band in SPEND_WARNINGS
                    if read and spend * 100 >= band * appetite_spend), None)
    return {"exhausted": bool(reasons), "reason": "+".join(reasons),
            "elapsed_minutes": round(elapsed_minutes, 2), "units_done": units_done,
            "appetite_minutes": appetite_minutes, "appetite_units": appetite_units,
            "appetite_spend": appetite_spend, "spend": spend, "spend_warning": warning,
            "spend_unread": spend_unread, "spend_includes_subagents": spend_includes_subagents}


def elapsed_minutes(started_at: str | None, now: datetime | None = None) -> float:
    """Wall-clock minutes since the run opened. 0 when the run was never opened (no start
    time is fabricated - the breaker cannot fire on a run that does not exist). Clamped at 0
    so clock skew on a shared checkout cannot report a negative spend."""
    if not started_at:
        return 0.0
    # The SHARED reader - see `sdlc_md.parse_iso8601`. A hand-rolled Z-only pattern here meant
    # the breaker read a run opened with an offset-bearing stamp as never opened, and reported
    # zero minutes spent on a run that had been going for hours.
    start = sdlc_md.parse_iso8601(started_at)
    if start is None:
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


def _resolve_spend_appetite(root: Path, args: argparse.Namespace) -> tuple[int, str | None]:
    """The spend appetite in force, in priced input-equivalent tokens, most specific first:
    `--appetite-spend`, then the run's `appetite.spend`, then config `appetite.spend`, then
    config `capacity.spend`, then 0 (unbounded). The flag and the run's value are honoured
    even at 0; a config key at 0 falls through to the next.

    Returns `(appetite, None)`, or `(0, why)` when the value that decides is one
    `run_state.spend_value` cannot read: spend is then unjudged and says why, and minutes and
    units still judge, rather than a malformed key stopping the breaker."""
    flag = getattr(args, "appetite_spend", None)
    if flag is not None:
        return int(flag), None
    declared = (run_state.read(root).get("appetite") or {}).get("spend")
    if declared is not None:
        return _spend_ceiling(declared, "the run's appetite.spend")
    for key in ("appetite.spend", "capacity.spend"):
        raw = config.get(root, key, 0)
        if raw:
            return _spend_ceiling(raw, f"config {key}")
    return 0, None


def _spend_ceiling(raw, where: str) -> tuple[int, str | None]:
    """`raw` as a spend appetite, or 0 with the sentence naming `where` it could not be read."""
    value = run_state.spend_value(raw)
    if value is None:
        return 0, (f"{where} is {raw!r}, not a whole number of {run_state.PRICED_LABEL} "
                   f"(write a plain integer: YAML reads 5e6 as text)")
    return value, None


def _spend_text(v: dict) -> str:
    """The spend half of a budget line, or "" when the spend axis judged nothing."""
    if v["spend"] is None:
        return ""
    return f", spend {v['spend']:,}/{v['appetite_spend']:,} {run_state.PRICED_LABEL}"


def _spend_notes(v: dict) -> None:
    """The spend axis's own lines under a budget line: why it was not judged, the warning band
    it has passed, and a reading that holds the main thread alone."""
    if v["spend_unread"]:
        print(f"spend: NOT JUDGED at this boundary - {v['spend_unread']}; minutes and units "
              f"still judge")
    if v["spend_warning"] and not v["exhausted"]:
        print(f"WARNING: spend has passed {v['spend_warning']}% of its appetite: "
              f"{v['spend']:,} of {v['appetite_spend']:,} {run_state.PRICED_LABEL} "
              f"({v['spend'] * 100 // v['appetite_spend']}%)")
    if v["spend_includes_subagents"] is False:
        print("spend: the reading holds the main thread only (no subagent transcript was "
              "read), so any delegated spend is not in it")


def _root(args: argparse.Namespace) -> Path:
    """The project root every path in this invocation anchors on.

    One answer per invocation, shared by the state file and the appetite breaker: two
    idioms in one script is how a writer and a reader end up disagreeing about which
    project they are working on.
    """
    return verify_ac.resolve_root(args)


def _state_path(args: argparse.Namespace) -> Path:
    """Where the guardrail state lives, anchored on the RESOLVED root.

    `Path(args.root)` honoured a named root but took the family default `.` as the cwd, so
    `record` from any subdirectory wrote a stray `<cwd>/sdlc-studio/.local/loop-state.json`
    and exited 0. The handoff reads `<root>/sdlc-studio/.local/loop-state.json`, so the
    attempts and failure signatures it exists to carry were written where it never looks.
    A relative `--state` anchors on the same root; an absolute one is honoured as given.
    """
    root = _root(args)
    if args.state:
        return verify_ac.under_root(root, args.state)
    return root / "sdlc-studio" / ".local" / "loop-state.json"


def cmd_record(args: argparse.Namespace) -> int:
    """Record a failed attempt, persist state, exit 3 if the unit quarantines."""
    path = _state_path(args)
    path.parent.mkdir(parents=True, exist_ok=True)
    state = sdlc_md.read_json(path, {"units": {}})
    state = record_attempt(state, args.unit, args.signature)
    v = verdict(state, args.unit, cap=args.cap, repeat=args.repeat)
    sdlc_md.atomic_write(path, json.dumps(state, indent=2))  # atomic: a crash mid-write must not reset guardrail state
    # The resolved path is printed on every verdict: a verdict that names no destination
    # looks the same whether the state landed where the handoff reads it or beside the cwd.
    if getattr(args, "format", "text") == "json":
        print(json.dumps({**v, "state": str(path)}, indent=2))
        return QUARANTINE_EXIT if v["quarantine"] else 0
    if v["quarantine"]:
        print(f"{args.unit}: QUARANTINE after {v['attempts']} attempts "
              f"(reason={v['reason']}) -> mark Blocked, continue [state: {path}]")
        return QUARANTINE_EXIT
    print(f"{args.unit}: continue ({v['attempts']} attempt(s), under guardrails) "
          f"[state: {path}]")
    return 0


def cmd_status(args: argparse.Namespace) -> int:
    """Print the current guardrail verdict for a unit."""
    path = _state_path(args)
    state = sdlc_md.read_json(path, {"units": {}})
    v = verdict(state, args.unit, cap=args.cap, repeat=args.repeat)
    print(json.dumps({**v, "state": str(path)}, indent=2))
    return 0


def cmd_budget(args: argparse.Namespace) -> int:
    """Evaluate the run's appetite at a unit boundary; exit BUDGET_EXIT when it is spent.

    Marks nothing: unlike `record`, a spent budget writes no state - the units keep their true
    status and the run stops cleanly; a spend read may refresh only the meter's parse memo
    (`run_state.spend_now`). The loop calls this BETWEEN units, so the appetite is honoured at
    a boundary and no unit is abandoned mid-implementation.

    Anchored on the same resolved root as the state file: read from the cwd, a run opened
    above this directory produced no run state at all, and an appetite the breaker never
    found reported as no appetite declared - a spent ceiling reading as `continue`."""
    root = _root(args)
    try:
        state = run_state.read(root)
    except run_state.RunStateError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    minutes, units = _resolve_appetite(root, args)
    spend_cap, unreadable = _resolve_spend_appetite(root, args)
    elapsed = elapsed_minutes(state.get("started_at"))
    done = units_consumed(root, state.get("batch") or [])
    # The meter is read only for a declared spend appetite: a read costs a transcript parse.
    got = (run_state.spend_now(root, state) if spend_cap else
           {"priced": None, "includes_subagents": None, "reason": unreadable})
    v = budget_verdict(minutes, units, elapsed, done, appetite_spend=spend_cap,
                       spend=got["priced"], spend_unread=got["reason"],
                       spend_includes_subagents=None if got["reason"] else
                       got["includes_subagents"])
    v["run_id"] = state.get("run_id")
    if getattr(args, "format", "text") == "json":
        print(json.dumps(v, indent=2))
        return BUDGET_EXIT if v["exhausted"] else 0
    if v["exhausted"]:
        print(f"appetite SPENT (reason={v['reason']}): {v['elapsed_minutes']} min elapsed"
              f"{f'/{minutes} budget' if minutes else ''}, {done} unit(s) done"
              f"{f'/{units} budget' if units else ''}{_spend_text(v)} -> stop cleanly: the "
              f"units already dispatched finish and no further unit starts; close the run and "
              f"sign its report (sprint.py close, then sprint.py sign), which hands over what is "
              f"left; units keep their true status")
        _spend_notes(v)
        return BUDGET_EXIT
    if not minutes and not units and not spend_cap and not unreadable:
        print(f"no appetite declared - run is unbounded ({v['elapsed_minutes']} min, "
              f"{done} unit(s) done)")
        return 0
    print(f"appetite OK: {v['elapsed_minutes']} min"
          f"{f'/{minutes}' if minutes else ''}, {done} unit(s) done"
          f"{f'/{units}' if units else ''}{_spend_text(v)} - continue")
    _spend_notes(v)
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
    b.add_argument("--appetite-spend", type=int, default=None, dest="appetite_spend",
                   help="spend ceiling in priced input-equivalent tokens; overrides the "
                        "declared/config appetite (0 = unbounded)")
    b.add_argument("--root", default=".", help="Repo root (default: .)")
    sdlc_md.add_format_arg(b)
    b.set_defaults(func=cmd_budget)
    sdlc_md.add_global_root(parser)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    # Resolve the root ONCE and write it back, so every verb below anchors on the tree the
    # run belongs to, not on the cwd the run happened to start in. Per-verb resolution is
    # left in place; this makes the anchor true of a verb that forgets to ask.
    args.root = str(verify_ac.resolve_root(args))
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
