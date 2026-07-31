# BG0467: The commit gate's test selection reached nothing: the handover was deleted before it was read, so every commit ran the whole suite

> **Status:** Fixed
> **Verification depth:** functional (each repair verified by restoring the defect as a mutant: the handover deleted before the read, the selection not passed to the runner, the runner ignoring a selection it was given, selected runs judged against the full peak, selected counts polluting the full series, selection outranking the loader-error fact, the budget reading the full series regardless, the series marker unwritten, and a selected total reported without saying so. Nine mutants, all KILLED - one only after it exposed that my own behavioural test named a module in the wrong directory and was SKIPPING, which reads as a pass)
> **Severity:** High
> **Points:** 3
> **Affects:** .githooks/commit-msg, tools/skill-tests.sh, tools/gate_timing.py, tools/tests/test_precommit_selection.py, tools/tests/test_gate_timing.py, tools/tests/test_precommit_lane_order.py
> **Evidence:** Found by the independent design review of CR0510. Confirmed in this repo's own telemetry before repair: `total.tests` reads 6,152 to 6,174 across all ten recorded runs, which is the full suite on every commit.
> **Created:** 2026-07-31
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5; human; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

`.githooks/commit-msg` deleted the pre-commit handover file and then read the computed test selectors out of that same file forty lines later. `selectors` was therefore ALWAYS empty, the run recorded `verdict-mode full`, and neither suite runner accepted a selector in any case.

Several hundred lines of selection logic - `select_tests`, `suite_read_map`, `_import_graph`, `test_relevant_paths`, with a long docstring about vacuous greens - ran on every commit, produced an answer, and the answer was discarded. The two unit suites are 86% of a 557s gate, so this one ordering paid for the whole of it.

Two further defects fell out of repairing it, both in the same family of a measurement that stops meaning what it says.

The SCOPE FLOOR refuses to record a total when a run covers less than 80% of the historic peak - the protection that keeps a truncated or half-imported suite out of a series only comparable between like runs. A selected run looks identical to that, so the first selected commit reported `total NOT recorded - 1171 tests against a peak of 6174` and the budget would have stopped being written at exactly the moment the gate got cheaper.

The BUDGET LINE then read the full series after a selected run, so a commit that took 226s was reported as `OVER - 554s`, which is the previous full run's duration presented as this one's. A budget line naming a number the commit did not pay is worse than none, because it is believed.

## Steps to Reproduce

Before the repair, from the recorded telemetry:

```text
total.tests: 6152 6152 6152 6152 6152 6162 6168 6174 6174 6174
total:        515  502  502  548  548  548  549  552  554  557
```

The count is the full suite on every run. `gate-suite-verdict.json` records `mode: full` for the same reason: the mode is derived from the same empty `selectors`.

In the hook: `rm -f "$handoff"` at one line, `selectors="$(sed -n 's/^suite-selector=//p' "$handoff" ...)"` forty lines later.

After the repair, measured across three commits on this repo:

```text
skill-tests   332s -> 30s
total         554s -> 226s -> 130s
budget line   OVER - 554s  ->  130s of a 380s budget [selected run], -59% since baseline
```

## Proposed Fix

Read the handover before deleting it, and pass the selection to both runners as dotted module names with the tests directory on `PYTHONPATH` - `unittest` refuses a file path, and running from inside the tests directory would move the cwd every fixture resolves against. Absence still means run everything, because a missing list is an unanswered question and never an answer of "nothing to run".

Exempt a selected run from the PEAK comparison but not from the loader-error check: selection relaxes a threshold, never a fact, and a selected run whose module failed to import is exactly as broken as a full one. Record its total in its own series, because the history is a rolling window and a stretch of selected commits would otherwise evict every full count until the peak collapsed to a subset's.

Have the budget report the series the run actually used, and say when it is a selected one so its drift is not taken for a like-for-like comparison against the full-run baseline.

## Acceptance Criteria

### AC1: the selection reaches the runners

- **Given** a selection of one test module handed to the shipped skill runner
- **When** it runs
- **Then** it runs that module's tests rather than the whole suite, and the handover is read before it is deleted - it was deleted forty lines before the read, so `selectors` was always empty and every commit ran everything
- **Verify:** pytest tools/tests/test_precommit_selection.py::SelectionReachesTheRunnersTests::test_a_selected_run_runs_FEWER_tests_than_the_full_suite
- **Verified:** yes (2026-07-31)

### AC2: a selected run is exempt from the peak, never from the fact

- **Given** a selected run covering a fraction of the historic peak, and separately one whose module failed to import
- **When** the scope floor judges each
- **Then** the first records and the second is refused, because selection relaxes a threshold and never a fact; and the selected counts go in their own series, since the history is a rolling window and a stretch of selected commits would otherwise evict every full count until the peak collapsed to a subset's
- **Verify:** pytest tools/tests/test_gate_timing.py::ScopeTests::test_a_SELECTED_run_is_not_judged_against_the_full_peak
- **Verified:** yes (2026-07-31)

### AC3: the budget reports the run that actually happened

- **Given** a selected commit following a full one
- **When** the budget line is printed
- **Then** it names the selected duration and marks it as such, rather than reporting the previous full run's - a budget line naming a number the commit did not pay is worse than none, because it is believed
- **Verify:** pytest tools/tests/test_gate_timing.py::ScopeTests::test_the_budget_reports_the_series_the_run_ACTUALLY_used
- **Verified:** yes (2026-07-31)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-31 | Claude Opus 5 | Filed - AFTER the diff, which is the wrong order and breaks this repo's own non-negotiable rule that work becomes a unit before it becomes a diff. Three commits referenced BG0467 before it existed. Recorded rather than backdated: the engagement floor exists to catch exactly this, and it was the author of the process-discipline work who broke it. |
