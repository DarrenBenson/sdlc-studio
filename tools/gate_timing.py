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
    # Which series the most recent per-commit TOTAL went into. Written here, where the fact is
    # known, so the budget report reads what actually happened rather than inferring it from
    # two series' lengths - an inference that cannot tell "selected ran last" from "selected
    # ran once, a while ago".
    if suite in ("total", "total.selected"):
        data["total.last_series"] = "selected" if suite == "total.selected" else "full"
    path = root / REL
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")
    return data


#: A run may lose this fraction of the historic peak test count and still be treated as having
#: run its scope. Deliberately generous: tests are legitimately deleted (US0284 deleted one), and
#: a floor that fires on real deletions would train people to ignore it. It exists for the case
#: where a chunk of the suite silently did not run at all.
SCOPE_FLOOR = 0.8

#: Below this fraction of the historic peak the run has not drifted, it has COLLAPSED, and the
#: commit is BLOCKED rather than merely unrecorded (BG0413). The two thresholds answer different
#: questions and must not be merged: 0.8 is "is this run comparable enough to time?", which is
#: deliberately generous because tests are legitimately deleted; this one is "did most of the
#: suite stop running?", which no other guard in the repo can notice. RUN-01KYNKDP ran 510 of
#: 5,645 tests - a 91% loss - and landed green, because a deleted test cannot fail.
COLLAPSE_FLOOR = 0.5

#: A deliberate bulk removal states itself here rather than being waved through: a JSON object
#: under `sdlc-studio/` carrying the expected post-removal count and the reason for it. It is
#: spent on the removal it describes - an ack naming a different count licenses nothing - so a
#: stale file cannot quietly become a standing exemption.
COLLAPSE_ACK = ".scope-collapse-ack.json"


def _collapse_ack(root: Path, tests: int) -> str | None:
    """The recorded reason a collapse to `tests` was deliberate, or None.

    Refuses an ack it cannot fully establish: unreadable, not an object, naming a different
    count, or carrying an empty reason. An escape that fails open is not an escape, it is the
    hole the guard was built to close.
    """
    path = Path(root) / "sdlc-studio" / COLLAPSE_ACK
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    if not isinstance(data, dict):
        return None
    reason = str(data.get("reason") or "").strip()
    if not reason:
        return None
    try:
        acked = int(data.get("tests"))
    except (TypeError, ValueError):
        return None
    return reason if acked == int(tests) else None


def scope_ok(root: Path, suite: str, tests: int, loader_error: bool = False,
             selected: bool = False) -> dict:
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
    elif selected:
        # A SELECTED run legitimately runs a fraction of the suite, so the peak comparison
        # cannot tell it from the truncated run this floor exists to catch. Judging it against
        # the full-suite peak would refuse to record every selected commit, which is how the
        # budget series would quietly stop being written at the moment selection started
        # working. The loader-error check above still applies - that is a FACT about the run
        # rather than a threshold, and a selected run whose module failed to import is exactly
        # as broken as a full one. Comparability is preserved by the caller recording a
        # selected total in its OWN series rather than beside the full ones.
        ok, why = True, f"{tests} tests in a SELECTED run - not compared against the full peak"
    elif peak is None:
        ok, why = True, "no test-count history yet - starting the series"
    elif tests < peak * SCOPE_FLOOR:
        ok, why = False, (f"{tests} tests ran against a peak of {int(peak)} "
                          f"({tests / peak:.0%}, floor {SCOPE_FLOOR:.0%})")
    else:
        ok, why = True, f"{tests} tests against a peak of {int(peak)}"
    # Graded SEPARATELY from `ok`, and only where a peak exists to collapse against. A selected
    # run legitimately runs a fraction of the suite, and a loader error is a different fact with
    # its own consequence - both are refused above without being called a collapse, because
    # blocking either would fire on ordinary events and train the bypass.
    collapsed = False
    if peak is not None and not selected and not loader_error and tests < peak * COLLAPSE_FLOOR:
        drop = 1 - tests / peak
        reason = _collapse_ack(root, tests)
        # `is not None`, not truthiness. An empty reason is refused by `_collapse_ack` itself,
        # and a truthy test here would ALSO reject it - which reads as defence in depth but is
        # not: it makes the explicit guard unreachable, so deleting it changes no behaviour and
        # no test can tell. Mutation caught exactly that; the emptiness rule now has one owner.
        if reason is not None:
            # The ack clears the COLLAPSE grade and NOTHING ELSE. `ok` stays False, because the
            # 0.8 floor answers a different question - is this run comparable enough to TIME? -
            # and a deliberately shrunk suite is not. Setting `ok = True` here let a 1-test run's
            # duration into the budget series, where it read as a 100% improvement: BG0239's
            # exact regression, reintroduced through the new escape.
            why = (f"{tests} tests against a peak of {int(peak)} - a {drop:.0%} drop, "
                   f"acknowledged as deliberate: {reason}. Not recorded: an acknowledged "
                   f"shrink is still not comparable with the runs before it")
        else:
            collapsed = True
            # `ok` is ALREADY False here and is not reassigned: COLLAPSE_FLOOR (0.5) is below
            # SCOPE_FLOOR (0.8), so every collapsed count has failed the floor above. Setting it
            # again read as defence in depth and was provably unreachable-as-behaviour - the
            # same dead-guard shape the comment forty lines below condemns, found by an
            # independent seat whose mutant deleting it survived.
            # A count of zero is reported as its own state. It is still a collapse - nobody can
            # tell "the suite ran nothing" from "nothing could be counted", and neither is
            # evidence the scope ran - but the two have very different fixes, and a reader
            # chasing a "100% drop" while the real fault is a changed runner output format
            # would be looking in the wrong place.
            cause = ("no test count was parsed from the run at all, so either the suite ran "
                     "nothing or the runner's output format changed"
                     if tests == 0 else
                     f"a {drop:.0%} drop, and a deleted test cannot fail, so most of this "
                     f"suite may have stopped running")
            why = (f"{tests} tests ran against a peak of {int(peak)} - {cause}. "
                   f"If the removal is deliberate, record it in "
                   f"sdlc-studio/{COLLAPSE_ACK} as "
                   f'{{"tests": {tests}, "reason": "<why>"}}')
    return {"ok": ok, "why": why, "tests": tests, "peak": peak, "collapsed": collapsed}


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


def _ran_selected(root: Path) -> bool:
    """Did the most recent run record a SELECTED total rather than a full one?

    Read from the marker `record` writes at the moment it writes the total, because that is
    where the fact is known. A repo that has never run selected has no marker and reads False,
    so the report behaves exactly as it did before.
    """
    return _load(root).get("total.last_series") == "selected"


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
    # Read the series this commit ACTUALLY ran in. A selected run records into
    # `total.selected`, so reading `total` unconditionally reported the last FULL run's
    # duration after a cheap commit - the first selected commit ran in 226s and the line said
    # `OVER - 554s`, which is a measurement describing a different commit. A budget report that
    # names a number this run did not pay is worse than none, because it is believed.
    selected = latest(root, "total.selected")
    full = latest(root, "total")
    measured, series = (selected, "selected") if _ran_selected(root) else (full, "full")
    if measured is None:
        return None
    # THE FULL SUITE IS JUDGED AGAINST ITS OWN CEILING, not the per-commit one. The full series
    # WAS read - `latest(root, "total")` whenever the last run was not selected - but it was
    # compared to `gate_budget.seconds`, a figure declared for a commit. A ~899s full run
    # against a 380s per-commit ceiling reads OVER as a matter of course, so the verdict carried
    # no information and nothing watched the number that actually grew: ~630s to ~899s at 6,610
    # to 7,417 tests (BG0594). An undeclared full-suite ceiling leaves the lane silent about the
    # full series rather than inventing a default.
    fallback = False
    if series == "full":
        # A DECLARED full-suite ceiling wins. Absent, the per-commit one is still used - going
        # SILENT here would drop the budget line entirely for every project that declares only
        # `seconds` and never runs selected, which is a regression, and two existing tests said
        # so. But the comparison is then apples to oranges, and an unlabelled mis-comparison is
        # the defect BG0594 is about: a ~899s full run against a 380s per-commit ceiling reads
        # OVER as a matter of course. So it falls back and SAYS it fell back, naming the key
        # that would judge it on its own terms.
        try:
            budget = float(block.get("full_seconds"))
        except (TypeError, ValueError):
            fallback = True
    # The baseline follows the CEILING, including into the fallback: reading
    # `full_baseline_seconds` while falling back to the per-commit ceiling dropped the drift
    # clause entirely, so the line lost the trend it exists to show. One decision, not two.
    own_series = (series == "full") and not fallback
    baseline = block.get("full_baseline_seconds" if own_series else "baseline_seconds")
    when = block.get("full_baseline_date" if own_series else "baseline_date")
    # THE VERDICT LEADS, and the seconds follow it. The line used to open with a total against
    # a seconds budget and append the rate verdict last, so the figure a reader took away was
    # the one the tool does not judge on: a total is selection width times cost-per-test, and
    # width varies continuously here. Order is not presentation - the first clause is what gets
    # quoted into a commit message and remembered.
    tests = latest(root, "total.selected.tests" if series == "selected" else "total.tests")
    rate = (measured / tests) if tests else None
    # DECLARED AS A RATE, never derived from the run's own width. Dividing the seconds ceiling
    # by the CURRENT run's test count gives every run its own ceiling, so the comparison is
    # tautological and two runs at identical cost still disagree - the first cut did exactly
    # that and its own test caught it. The rate is the quantity being budgeted, so it is the
    # quantity declared.
    try:
        ceiling_rate = float(block.get("rate_seconds_per_test"))
    except (TypeError, ValueError):
        ceiling_rate = None
    over = measured > budget
    rate_verdict = None
    if rate is not None and ceiling_rate:
        over = rate > ceiling_rate
        rate_verdict = {"rate": rate, "ceiling_rate": ceiling_rate}
        detail = (f"rate {rate:.3f}s/test vs a {ceiling_rate:.3f} ceiling - "
                  f"{'OVER' if over else 'under'}")
        if over:
            detail += " - REGRESSION: the per-test cost rose, whatever the total did"
        detail += f"; {measured:.0f}s of a {budget:.0f}s budget over {tests:.0f} tests"
    else:
        detail = f"{measured:.0f}s of a {budget:.0f}s budget"
        if rate is not None:
            # No declared rate ceiling: the raw total still decides, and the line SAYS the
            # verdict is width-sensitive rather than leaving a reader to take it for a
            # like-for-like one.
            detail += (f", {rate:.3f}s/test over {tests:.0f} tests [no "
                       f"`gate_budget.rate_seconds_per_test` declared - this verdict is on the "
                       f"raw total and moves with selection width]")
        else:
            # NO TEST COUNT AT ALL, and this is the line a reader cannot calibrate. Every other
            # branch carries its width; this one carried a bare total, so the one figure with
            # no denominator was the only one that never said so.
            detail += " over a selection width this run did not record"
            if ceiling_rate:
                # A rate ceiling IS declared and the rate cannot be computed, so the raw total
                # decides after all. Labelled on the same terms as its neighbour: the
                # inconsistency an unlabelled mis-comparison always turns out to be.
                detail += (" [a rate ceiling is declared but this run recorded no test count, "
                           "so the verdict falls back to the raw total and moves with "
                           "selection width]")
    if series == "selected":
        # Named, because a selected total is not comparable with the full-run baseline below
        # and a reader must not take the drift figure for a like-for-like one.
        detail += " [selected run]"
    elif fallback:
        detail += (" [FULL run judged against the per-commit ceiling - declare "
                   "`gate_budget.full_seconds` to judge it on its own terms]")
    if baseline is not None and when:
        # THE TREND, and only where a trend can honestly be computed. Reporting only "under
        # budget" is how a module grew 28% in two days without anyone noticing: it was under
        # every ceiling the whole time. But a PERCENTAGE between two totals measured at
        # different selection widths is a number about the widths, not about the cost - and the
        # baseline recorded here carries no width at all, so on a SELECTED run - whose width
        # moves commit to commit - the clause was stating a change nobody had measured. The
        # percentage is withheld exactly there. A full run judged on its OWN series is
        # like-for-like even with the count unrecorded, and keeps its percentage. The FALLBACK
        # path is not: it compares a whole-suite total against the per-commit baseline, a
        # measured +184% for a 7,400-test run against a ~1,400-test baseline, which is the
        # cross-population number this unit exists to remove. The first cut exempted it along
        # with the own-series full run and said in a comment that both were like-for-like -
        # true of one shape and false of the other, and a review executed the difference.
        # BOTH config reads are guarded, on the same terms as every other float in this
        # function: a bad config is advisory here and never a commit failure. An unguarded
        # `float()` on a hand-declared key raised, the command exited with a traceback, and the
        # hook swallows this line's stderr - so the whole budget report vanished with no
        # diagnostic, which is the one outcome the module docstring promises against.
        try:
            base_tests = float(block.get("full_baseline_tests" if own_series
                                         else "baseline_tests"))
        except (TypeError, ValueError):
            base_tests = None
        try:
            base_s = float(baseline)
        except (TypeError, ValueError):
            base_s = None
        if base_s is None:
            detail += f" (baseline {baseline}s on {when})"
        elif base_tests or own_series:
            drift = (measured - base_s) / base_s * 100.0
            width = (f" over {base_tests:.0f} tests" if base_tests else "")
            detail += (f" (baseline {base_s:.0f}s on {when}{width}, {drift:+.0f}% since)")
        else:
            here = f"{tests:.0f}" if tests else "an unrecorded number of"
            # NAMES THE KEY that restores the figure, on the same terms as the two disclosures
            # above it: a clause that explains a withholding without saying what to declare
            # leaves the reader knowing only that something is missing.
            key = "full_baseline_tests" if own_series else "baseline_tests"
            detail += (f" (baseline {base_s:.0f}s on {when} over an unrecorded width, against "
                       f"{here} tests here - no percentage is stated, because a change between "
                       f"two widths is a number about the widths. Declare "
                       f"`gate_budget.{key}` to restore it)")
    return {"measured": measured, "budget": budget, "baseline": baseline,
            "baseline_date": when, "over": over, "detail": detail,
            "rate": rate, "rate_verdict": rate_verdict}


def cmd_record(args: argparse.Namespace) -> int:
    record(Path(args.root), args.suite, args.seconds)
    return 0


def cmd_scope(args: argparse.Namespace) -> int:
    """Judge whether a run covered its scope, then record its test count.

    Exit 0 = the run is comparable and its total may be recorded; exit 1 = it only got invoked;
    exit 3 = the suite COLLAPSED and the commit must be blocked.

    THREE, not two: python itself exits 2 for an argparse error and for a missing script file,
    so a caller reading 2 as "collapsed" blocks the commit when the tool is absent or
    mis-invoked - the opposite of this hook's promise to degrade honestly. 3 is a code python
    will not produce on our behalf.

    A DRIFT (exit 1) appends the count, so the peak keeps improving and one short run does not
    poison the series. A COLLAPSE does NOT: the refusal text says "commit again", the history is
    a rolling window of 10, and appending here meant ten retries evicted every real count and
    left the peak at the collapsed value - disabling the guard permanently, and with a zero
    count disabling the 0.8 floor with it.

    Never raises into a commit; the caller decides what an exit code costs.
    """
    root = Path(args.root)
    selected = bool(getattr(args, "selected", False))
    verdict = scope_ok(root, args.suite, args.tests, args.loader_error, selected=selected)
    # A selected run's counts go in their own series. The peak is a `max`, so one selected
    # count mixed in is harmless TODAY - but the history is a rolling window of HISTORY runs,
    # so a stretch of selected commits evicts every full count and the peak collapses to a
    # selected one. The floor would then be judging full runs against a subset's count, which
    # is the erosion this separation prevents. Stated as the eviction it is, rather than as an
    # immediate drag it is not.
    suffix = ".selected" if selected else ""
    if verdict["collapsed"]:
        # NOT recorded. The refusal says "commit again", the history is a rolling window of 10,
        # and appending here meant ten retries evicted every real count and left the peak at the
        # collapsed value - the guard then permanently off, and with a zero count the 0.8 floor
        # off with it. A drift still records, which is what lets a real peak recover.
        print(f"gate-budget: suite scope COLLAPSED, commit BLOCKED - {verdict['why']}")
        return 3
    record(root, f"{args.suite}{suffix}.tests", args.tests)
    if not verdict["ok"]:
        # Said out loud on BOTH refusing paths, and on the acknowledged one too: an escape that
        # is taken silently is indistinguishable from a guard that never fired.
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
    # The verdict word ONCE. Where a rate ceiling is declared the detail leads with its own
    # `- OVER` / `- under`, and prefixing there printed `OVER - rate ... - OVER - REGRESSION`:
    # the first thing a reader meets on every commit, stuttering.
    lead = "OVER - " if rep["over"] and not rep.get("rate_verdict") else ""
    print(f"gate-budget: {lead}{rep['detail']}")
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
    s.add_argument("--selected", action="store_true",
                   help="the run was a SELECTED subset, so its count is not comparable with the "
                        "full-suite peak and is recorded in its own series")
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
