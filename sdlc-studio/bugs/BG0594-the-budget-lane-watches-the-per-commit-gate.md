# BG0594: the budget lane watches the per-commit gate only, so the full suite grew 46% unobserved

> **Status:** Open
> **Severity:** Medium
> **Points:** 2
> **Affects:** tools/gate_timing.py, tools/tests/test_gate_timing.py
> **Created:** 2026-08-18
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

`gate_budget` compares the latest PER-COMMIT total against a single declared ceiling, and that population is BIMODAL by selection width, so one scalar cannot describe it. A narrow commit selects ~1,400 tests and costs ~212s; a wide one selects ~5,100 and costs ~540s. The 380s ceiling sits BETWEEN the two modes, so it reports OVER on every wide commit and comfortable headroom on every narrow one, and is right about neither. Separately, nothing compares the FULL suite against anything, and that is the figure that genuinely grew: ~630s to ~921s, roughly +46%. That growth is paid at every push, release and close, and it is the cost that actually rose. An unwatched cost is one that gets noticed when a timeout kills a commit, which BG0579 already recorded happening once at a 600s ceiling with everything left staged.

## Steps to Reproduce

Measured 2026-08-18 from `sdlc-studio/.local/gate-timings.json`, reading `total.selected` BESIDE `total.selected.tests` - which is the pairing that makes the series legible and which the first cut of this filing did not do:

| tests selected | seconds | s/test |
| --- | --- | --- |
| 1,074 | 184 | 0.171 |
| 1,418 | 212 | 0.150 |
| 1,418 | 212 | 0.150 |
| 1,418 | 212 | 0.150 |
| 1,428 | 221 | 0.155 |
| 1,428 | 232 | 0.162 |
| 1,813 | 246 | 0.136 |
| 5,104 | 535 | 0.105 |
| 5,114 | 554 | 0.108 |
| 5,437 | 762 | 0.140 |

Two modes, not one series with an outlier: narrow median 212s over seven runs, wide median 554s over three. Per-test cost is stable across BOTH at 0.105-0.171 s/test, so the variance is entirely selection width and the quantity worth budgeting is the rate, not the total. `total` = [554, 626, 631, 626, 626, 632, 655, 649, 921, 922]. `tools/gate_timing.py` `budget_report` reads only the per-commit total, and `_ran_selected` merely labels which kind the latest row was; no code path compares the full-suite series to a declared figure. A second, smaller defect rides along: `budget_report` judges the LATEST row, so a legitimately wide commit makes the next reading look like a regression - the series is the signal and the lane reads one row.

## Proposed Fix

Declare and watch a second figure for the full suite, with its own baseline and date, in the same block so the number and the baseline it was chosen against stay together - that is the property the existing comment says a budget must have. Keep it ADVISORY like its sibling: a wall-clock check on a loaded machine must never refuse a correct commit. While there, consider judging the per-commit figure against a short trailing window rather than the single latest row, so selection width does not read as drift; the existing comment already warns that a single reading means little and the series is the signal, and the code does the opposite.

The staleness guard needs the same treatment and is the reason AC4 exists. `test_the_declared_budget_covers_the_measured_cost` asserts `baseline >= 250.0` against the LIVE config, a literal chosen in 2026-07 against a then-measured ~317s peak. A literal cannot track a bimodal population: 317 describes neither mode, the 380s ceiling is below the wide mode's median of 554, and the guard notices neither fact. Derive the floor from the recorded series - and index it to selection width - rather than pinning a number that was only ever true of one commit shape.

## Acceptance Criteria

- [ ] **AC1** Given a declared full-suite budget and a recorded full-suite series, when the budget lane reports, then it compares the latest full-suite total against that figure
- [ ] **AC2** Given no declared full-suite budget, when it reports, then it stays silent about the full suite rather than inventing a default
- [ ] **AC3** Given two per-commit runs of equal per-test cost but different selection width, when the lane judges them, then it reaches the same verdict for both - a wide commit is not a regression, and today it is the ONLY thing that reports one
- [ ] **AC4** Given a repository whose declared budget no longer describes its measured cost in either direction, when the staleness guard runs, then it says so - the guard currently asserts a literal floor (`baseline >= 250.0`) against the live config, which neither notices a ceiling that has fallen below the wide mode nor permits a baseline that has genuinely moved

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-18 | sdlc-studio | Filed |
| 2026-08-18 | sdlc-studio | AC3 and AC4 rewritten. The first cut read `total.selected` without `total.selected.tests` beside it, took the recent 212s rows as the current cost, and concluded the baseline should be re-declared DOWNWARD to 212. Two gate runs minutes later measured 535s and 554s. The series is bimodal by selection width, the 212s rows are narrow commits, and a downward re-baseline would have made every wide commit report OVER - the exact noise CR0420 removed once already. The guard that refused the change was right; the premise was mine |
