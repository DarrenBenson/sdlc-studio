# BG0594: the budget lane watches the per-commit gate only, so the full suite grew 43% against a ceiling declared for the other population

> **Status:** Open
> **Severity:** Medium
> **Points:** 3
> **Affects:** tools/gate_timing.py, tools/tests/test_gate_timing.py, .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py, sdlc-studio/.config.yaml
> **Created:** 2026-08-18
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

`gate_budget` compares ONE row of the per-commit series against a single declared ceiling, and
that population varies continuously with selection width, so one scalar cannot describe it. Per-test
cost is stable at 0.10-0.15 s/test across the whole range; the total is selection width times that
rate. The 380s ceiling therefore reports OVER on every wide commit and comfortable headroom on every
narrow one, and is right about neither. The full suite IS read - `budget_report` takes
`latest(root, "total")` whenever the last run was not selected - but it is judged against the SAME
per-commit ceiling, so a 899s full run is reported OVER a 380s budget as a matter of course and the
signal carries no information. The full suite is the figure that genuinely grew, ~630s to ~899s at
6,610 to 7,417 tests, and it is paid at every push, release and close.

CORRECTION, recorded rather than quietly dropped. The first cut of this filing asserted that "no
code path compares the full-suite series to a declared figure". That is FALSE: `gate_timing.py`
`budget_report` reads `full = latest(root, "total")` and uses it when `_ran_selected(root)` is
false. The defect is the CEILING it is compared to, not the absence of a comparison. The same cut
described the series as BIMODAL - "two modes, not one series with an outlier". Re-measured
2026-08-19, the window has moved and that reading no longer holds either: the selected series is
now [212, 212, 212, 554, 535, 635, 769, 701, 595, 295] against [1418, 1418, 1418, 5114, 5104, 5309,
5441, 5573, 5211, 3060] tests, and the 3,060-test run at 295s sits between the supposed modes. A
narrow window made a continuum look like two populations. Both errors were found by an adversarial
goal review of the sprint that would have built the fix, before any code was written.

## Steps to Reproduce

Re-measured 2026-08-19 from `sdlc-studio/.local/gate-timings.json`, reading `total.selected` BESIDE
`total.selected.tests` - the pairing that makes the series legible and which the first cut of this
filing did not do:

| tests selected | seconds | s/test |
| --- | --- | --- |
| 1,418 | 212 | 0.150 |
| 1,418 | 212 | 0.150 |
| 1,418 | 212 | 0.150 |
| 3,060 | 295 | 0.096 |
| 5,104 | 535 | 0.105 |
| 5,114 | 554 | 0.108 |
| 5,211 | 595 | 0.114 |
| 5,309 | 635 | 0.120 |
| 5,441 | 769 | 0.141 |
| 5,573 | 701 | 0.126 |

One series, ordered by width, with a stable per-test rate. The quantity worth budgeting is that
rate, not the total. The full-suite series over the same window is `total` = [626, 631, 626, 626,
632, 655, 649, 921, 922, 899] against `total.tests` = [6610, 6611, 6611, 6611, 6611, 6611, 6611,
7277, 7277, 7417]: +43% seconds for +12% tests, so the full suite's per-test cost rose while the
selected one did not. `budget_report` (tools/gate_timing.py) judges the LATEST row against
`gate_budget.seconds`, and picks the full series only when the last run was not selected - so which
population is judged depends on what the previous commit happened to touch, and both are judged
against a ceiling declared for one of them.

## Proposed Fix

Declare and watch a second figure for the full suite, with its own baseline and date, in the same block so the number and the baseline it was chosen against stay together - that is the property the existing comment says a budget must have. Keep it ADVISORY like its sibling: a wall-clock check on a loaded machine must never refuse a correct commit. While there, consider judging the per-commit figure against a short trailing window rather than the single latest row, so selection width does not read as drift; the existing comment already warns that a single reading means little and the series is the signal, and the code does the opposite.

The staleness guard needs the same treatment and is the reason AC4 exists. `test_the_declared_budget_covers_the_measured_cost` asserts `baseline >= 250.0` against the LIVE config, a literal chosen in 2026-07 against a then-measured ~317s peak. A literal cannot track a bimodal population: 317 describes neither mode, the 380s ceiling is below the wide mode's median of 554, and the guard notices neither fact. Derive the floor from the recorded series - and index it to selection width - rather than pinning a number that was only ever true of one commit shape.

## Acceptance Criteria

- [ ] **AC1** Given a per-commit series whose runs differ in selection width, when the budget lane reports, then it states the per-test rate beside the total, with a DECLARED tolerance - and that tolerance is shown to separate the two populations it must judge: measured 2026-08-19 over the ten runs the timings file then held - a dated snapshot, not a standing figure - the selected series' median rate is 0.1233 s/test with extremes 0.0964 and 0.1480 (-22% to +20%), while the full-suite rate rose 0.0947 to 0.1267 (+34%), so a band loose enough to absorb the first cannot be the band that flags the second
- [ ] **AC2** Given a full-suite run, when the lane reports on it, then it is judged against a full-suite figure DECLARED in `gate_budget:` with its own baseline and date, not against the per-commit ceiling: `budget_report` reads `latest(root, "total")` whenever the last run was not selected and compares it to `gate_budget.seconds`, so a 899s full run is permanently OVER a 380s budget and that verdict carries no information
- [ ] **AC3** Given two runs of equal per-test cost whose totals STRADDLE the declared ceiling - one above it, one below - when the lane judges them, then it reaches the same verdict for both; a fixture whose runs are both under the ceiling cannot see the defect, because a raw comparison already agrees there
- [ ] **AC4** Given a run whose per-test rate rose on a NARROWER selection, so its total fell, when the lane judges it, then it reports the regression - the control proving a rate-based verdict discriminates rather than excusing every total that happens to drop
- [ ] **AC5** Given a declared budget that no longer describes the measured cost in either direction, when the staleness derivation in `gate_timing.py` runs, then it reports the drift - the check belongs in production, where a mutant can be applied to it; today it is an assertion in `test_gate_timing.py` asserting a literal floor of 250.0, which neither notices a ceiling below the wide end of the series nor permits a baseline that has genuinely moved
- [ ] **AC6** Given `sprint.execution_cost`, whose docstring says "the measured cost of one full run", when a plan prints its execution policy, then the figure quoted for the close and release boundaries is a FULL-run measurement - today it returns the latest series whichever that is, which is why this run's own plan priced its close at ~295s against a recorded full series of ~899s

## Test Plan

| Criterion | Mutant - the production change this test must fail on | Title |
| --- | --- | --- |
| AC1 | in `gate_timing.py`, widen the declared tolerance until both series sit inside it | Given a per-commit series whose runs differ in selection width, when the budget lane reports, then it states the per-test rate beside the total, with a DECLARED tolerance - and that tolerance is shown to separate the two populations it must judge: measured 2026-08-19 over the ten runs the timings file then held - a dated snapshot, not a standing figure - the selected series' median rate is 0.1233 s/test with extremes 0.0964 and 0.1480 (-22% to +20%), while the full-suite rate rose 0.0947 to 0.1267 (+34%), so a band loose enough to absorb the first cannot be the band that flags the second |
| AC2 | in `gate_timing.py`, change the whole-suite branch to read the per-commit ceiling | Given a full-suite run, when the lane reports on it, then it is judged against a full-suite figure DECLARED in `gate_budget:` with its own baseline and date, not against the per-commit ceiling: `budget_report` reads `latest(root, "total")` whenever the last run was not selected and compares it to `gate_budget.seconds`, so a 899s full run is permanently OVER a 380s budget and that verdict carries no information |
| AC3 | in `gate_timing.py`, drop the normalisation and compare raw seconds | Given two runs of equal per-test cost whose totals STRADDLE the declared ceiling - one above it, one below - when the lane judges them, then it reaches the same verdict for both; a fixture whose runs are both under the ceiling cannot see the defect, because a raw comparison already agrees there |
| AC4 | in `gate_timing.py`, remove the regression branch and emit the total alone | Given a run whose per-test rate rose on a NARROWER selection, so its total fell, when the lane judges it, then it reports the regression - the control proving a rate-based verdict discriminates rather than excusing every total that happens to drop |
| AC5 | in `gate_timing.py`, make it return None when the measured series sits above the declared ceiling | Given a declared budget that no longer describes the measured cost in either direction, when the staleness derivation in `gate_timing.py` runs, then it reports the drift - the check belongs in production, where a mutant can be applied to it; today it is an assertion in `test_gate_timing.py` asserting a literal floor of 250.0, which neither notices a ceiling below the wide end of the series nor permits a baseline that has genuinely moved |
| AC6 | in `sprint.py`, return `measured_gate_seconds`' first element unconditionally | Given `sprint.execution_cost`, whose docstring says "the measured cost of one full run", when a plan prints its execution policy, then the figure quoted for the close and release boundaries is a FULL-run measurement - today it returns the latest series whichever that is, which is why this run's own plan priced its close at ~295s against a recorded full series of ~899s |

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-18 | sdlc-studio | Filed |
| 2026-08-18 | sdlc-studio | AC3 and AC4 rewritten. The first cut read `total.selected` without `total.selected.tests` beside it, took the recent 212s rows as the current cost, and concluded the baseline should be re-declared DOWNWARD to 212. Two gate runs minutes later measured 535s and 554s. The series is bimodal by selection width, the 212s rows are narrow commits, and a downward re-baseline would have made every wide commit report OVER - the exact noise CR0420 removed once already. The guard that refused the change was right; the premise was mine |
| 2026-08-19 | sdlc-studio | Premise CORRECTED: the full suite is read, against the wrong ceiling; the bimodality reading did not survive re-measurement |
| 2026-08-19 | sdlc-studio | Criteria re-authored against the corrected premise: the full suite IS read, against the wrong ceiling, and the series is a continuum rather than two modes |
| 2026-08-19 | sdlc-studio | Scope widened to `sprint.execution_cost`, whose docstring says "one FULL run" while it returns the latest SELECTED figure - the plan for this very run priced its close and release at ~295s against a recorded full series of ~899s. Re-pointed 2 -> 3 |
| 2026-08-19 | sdlc-studio | Plan review round 2: AC1's span restated from the live series as a RELATIVE spread per series, because an absolute band cannot separate the two populations and the margin is about six points |
