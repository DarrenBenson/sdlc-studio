#!/usr/bin/env python3
"""Test-suite runtime history for the pre-commit gate.

The gate's unit suite is the one guard that costs real wall-clock (~2,800 tests). A
guard paid for on every commit has to be predictable: an unannounced 2.5-minute run
exceeds common tool timeouts, so the commit looks hung and gets killed or bypassed -
and a bypassed guard guards nothing.

This records each run's wall-time to a small bounded history and estimates the next
one from it, so a long run is expected rather than a surprise. Advisory only: it
never fails a commit, and a missing or unreadable history degrades to silence rather
than to a wrong number.

Subcommands:
  record    append one run's duration for a suite
  estimate  print a warning line when the expected duration exceeds a threshold
"""
from __future__ import annotations

import argparse
import json
import statistics
import sys
from pathlib import Path

# Keep the history short: the last few runs on THIS machine predict the next one far
# better than a long tail spanning hardware changes and suite growth.
HISTORY = 10
REL = "sdlc-studio/.local/gate-timings.json"


def _load(root: Path) -> dict:
    """The timings file, or {} when absent/corrupt - never raise into a commit."""
    try:
        data = json.loads((root / REL).read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else {}
    except (OSError, ValueError):
        return {}


def record(root: Path, suite: str, seconds: float) -> dict:
    """Append `seconds` to `suite`'s history, keeping the most recent HISTORY runs."""
    data = _load(root)
    runs = [float(x) for x in data.get(suite, []) if isinstance(x, (int, float))]
    runs.append(round(float(seconds), 1))
    data[suite] = runs[-HISTORY:]
    path = root / REL
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")
    return data


#: A run may lose this fraction of the historic peak test count and still be treated as having
#: run its scope. Deliberately generous: tests are legitimately deleted (US0284 deleted one), and
#: a floor that fires on real deletions would train people to ignore it. It exists for the case
#: where a chunk of the suite silently did not run at all.
SCOPE_FLOOR = 0.8


def scope_ok(root: Path, suite: str, tests: int, loader_error: bool = False) -> dict:
    """Did this run actually run its scope, or did it only get invoked?

    The budget series is only comparable between runs that did the same work. BG0239: the hook set
    `suites_ran` once the lane was INVOKED, so a commit where a module failed to import recorded a
    short run as this commit's cost, and the budget read '-26% since' - a broken suite reading as
    an improvement, the same magnitude as the ratchet the lane exists to expose.

    Two signals, and NEITHER is the run's duration. Judging duration by duration history is
    circular, and it fails in the one direction that matters: the improvement shipped in EP0093
    took a commit from 196.7s to 99s, which any plausibility band over prior history would have
    rejected as implausible. A real speedup must never be discarded as noise.

    So:
    - `loader_error` - a module that failed to import. This is the filed reproduction exactly, and
      it is a fact rather than a threshold, so it is checked first and needs no history.
    - the test COUNT against the historic peak. Catches a lane that ran a fraction of its scope
      without erroring, which no single fact reveals.

    With no history the run is accepted: a fresh clone must be able to start a series, and
    refusing to record until a baseline exists means never recording one.
    """
    prior = [float(x) for x in _load(root).get(f"{suite}.tests", [])
             if isinstance(x, (int, float))]
    peak = max(prior) if prior else None
    if loader_error:
        ok, why = False, "a test module failed to import, so the suite ran only part of its scope"
    elif peak is None:
        ok, why = True, "no test-count history yet - starting the series"
    elif tests < peak * SCOPE_FLOOR:
        ok, why = False, (f"{tests} tests ran against a peak of {int(peak)} "
                          f"({tests / peak:.0%}, floor {SCOPE_FLOOR:.0%})")
    else:
        ok, why = True, f"{tests} tests against a peak of {int(peak)}"
    return {"ok": ok, "why": why, "tests": tests, "peak": peak}


def expected(root: Path, suite: str) -> float | None:
    """Median of the recorded runs, or None with no history.

    Median, not mean: one pathological run (a cold cache, a machine under load) should
    not move the estimate the developer is shown on every subsequent commit.
    """
    runs = [float(x) for x in _load(root).get(suite, []) if isinstance(x, (int, float))]
    return statistics.median(runs) if runs else None


def latest(root: Path, suite: str) -> float | None:
    """The MOST RECENT recorded run, or None with no history.

    Deliberately not the median. `expected` answers "how long should I expect to wait", where a
    median is right because it ignores one bad run. The budget answers "what does a commit cost
    NOW", and a median over a ten-run window lags a step change badly: when the suite went from
    ~153s to 79s the median still read ~152s, so a budget built on it would have reported a
    number that was true of no run that had happened for two commits.
    """
    runs = [float(x) for x in _load(root).get(suite, []) if isinstance(x, (int, float))]
    return runs[-1] if runs else None


# The budget is a DECLARATION a human made against a measured baseline, not a fitted constant -
# see RFC0048 D6. It is read from the project config so the number and the baseline it was
# chosen against live together; a number without its baseline is not reviewable later.
BUDGET_KEY = "gate_budget"


def budget_config(root: Path) -> dict | None:
    """The declared budget block, or None when the project has not set one."""
    try:
        import yaml
    except ImportError:
        return None
    try:
        cfg = yaml.safe_load((root / "sdlc-studio" / ".config.yaml").read_text(encoding="utf-8"))
    except Exception:  # noqa: BLE001 - a bad config is advisory here, never a commit failure
        return None
    block = (cfg or {}).get(BUDGET_KEY)
    return block if isinstance(block, dict) else None


def budget_report(root: Path) -> dict | None:
    """Compare the latest recorded per-commit total against the declared budget.

    Returns None when no budget is declared or nothing has been recorded yet - silence, never a
    guessed number. `over` is advisory in every case: a wall-clock check on a loaded or shared
    machine must never refuse a correct commit (RFC0048 D6, matching D3's advisory placement).
    """
    block = budget_config(root)
    if not block:
        return None
    try:
        budget = float(block.get("seconds"))
    except (TypeError, ValueError):
        return None
    measured = latest(root, "total")
    if measured is None:
        return None
    baseline = block.get("baseline_seconds")
    when = block.get("baseline_date")
    detail = f"{measured:.0f}s of a {budget:.0f}s budget"
    if baseline is not None and when:
        # The TREND, not just the instantaneous value. Reporting only "under budget" is how
        # test_gate.py grew 28% in two days without anyone noticing: it was under every ceiling
        # the whole time.
        try:
            drift = (measured - float(baseline)) / float(baseline) * 100.0
            detail += (f" (baseline {float(baseline):.0f}s on {when}, "
                       f"{drift:+.0f}% since)")
        except (TypeError, ValueError):
            detail += f" (baseline {baseline}s on {when})"
    return {"measured": measured, "budget": budget, "baseline": baseline,
            "baseline_date": when, "over": measured > budget, "detail": detail}


def cmd_record(args: argparse.Namespace) -> int:
    record(Path(args.root), args.suite, args.seconds)
    return 0


def cmd_scope(args: argparse.Namespace) -> int:
    """Judge whether a run covered its scope, then record its test count.

    Exit 0 = the run is comparable and its total may be recorded; exit 1 = it only got invoked.
    The count is appended either way, so the peak keeps improving and one truncated run does not
    poison the series. Never raises into a commit.
    """
    root = Path(args.root)
    verdict = scope_ok(root, args.suite, args.tests, args.loader_error)
    record(root, f"{args.suite}.tests", args.tests)
    if not verdict["ok"]:
        print(f"gate-budget: total NOT recorded - {verdict['why']}")
    return 0 if verdict["ok"] else 1


def cmd_estimate(args: argparse.Namespace) -> int:
    """Print the expected duration when it is worth announcing. Silent otherwise."""
    exp = expected(Path(args.root), args.suite)
    if exp is None:
        return 0                      # no history yet: say nothing rather than guess
    if exp >= args.warn_seconds:
        print(f"{args.suite}: expect ~{exp:.0f}s from the last "
              f"{len(_load(Path(args.root)).get(args.suite, []))} run(s) - "
              f"allow at least {int(exp * 2)}s of timeout")
    return 0


def cmd_budget(args: argparse.Namespace) -> int:
    """Report the per-commit total against the declared budget. ALWAYS returns 0: over budget is
    a warning, never a blocked commit."""
    rep = budget_report(Path(args.root))
    if rep is None:
        return 0                      # no budget declared, or nothing recorded yet: say nothing
    print(f"gate-budget: {'OVER - ' if rep['over'] else ''}{rep['detail']}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--root", default=".", help="repo root (default: .)")
    sub = p.add_subparsers(dest="cmd", required=True)

    r = sub.add_parser("record", help="append one run's duration")
    r.add_argument("--suite", required=True)
    r.add_argument("--seconds", type=float, required=True)
    r.set_defaults(func=cmd_record)

    s = sub.add_parser("scope", help="did the run cover its scope? (exit 1 if it only got invoked)")
    s.add_argument("--suite", required=True)
    s.add_argument("--tests", type=int, required=True)
    s.add_argument("--loader-error", action="store_true",
                   help="a test module failed to import, so the scope was truncated")
    s.set_defaults(func=cmd_scope)

    e = sub.add_parser("estimate", help="warn when the expected duration is long")
    e.add_argument("--suite", required=True)
    e.add_argument("--warn-seconds", type=float, default=60.0)
    e.set_defaults(func=cmd_estimate)

    b = sub.add_parser("budget", help="report the per-commit total against the declared budget")
    b.set_defaults(func=cmd_budget)
    return p


def main(argv=None) -> int:
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
