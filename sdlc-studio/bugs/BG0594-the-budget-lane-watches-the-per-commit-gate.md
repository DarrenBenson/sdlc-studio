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

`gate_budget` compares the latest PER-COMMIT total against a declared ceiling and nothing compares the FULL suite against anything. Over the same period the per-commit series stayed flat (median 216s, three most recent runs 212s, well under the 380s ceiling) while the full-suite series moved from ~630s to ~921s - roughly +46%. That growth is paid at every push, release and close, and it is the cost that actually rose. An unwatched cost is one that gets noticed when a timeout kills a commit, which BG0579 already recorded happening once at a 600s ceiling with everything left staged.

## Steps to Reproduce

Measured 2026-08-18 from `sdlc-studio/.local/gate-timings.json`. `total.selected` = [264, 147, 221, 184, 246, 232, 762, 212, 212, 212] - median 216, max 762 where that one reading is selection WIDTH (a commit selecting 102 test modules), not drift. `total` = [554, 626, 631, 626, 626, 632, 655, 649, 921, 922]. `tools/gate_timing.py` `budget_report` reads only the per-commit total, and `_ran_selected` merely labels which kind the latest row was; no code path compares the full-suite series to a declared figure. A second, smaller defect rides along: `budget_report` judges the LATEST row, so a legitimately wide commit makes the next reading look like a regression - the series is the signal and the lane reads one row.

## Proposed Fix

Declare and watch a second figure for the full suite, with its own baseline and date, in the same block so the number and the baseline it was chosen against stay together - that is the property the existing comment says a budget must have. Keep it ADVISORY like its sibling: a wall-clock check on a loaded machine must never refuse a correct commit. While there, consider judging the per-commit figure against a short trailing window rather than the single latest row, so selection width does not read as drift; the existing comment already warns that a single reading means little and the series is the signal, and the code does the opposite.

The staleness guard needs the same treatment and is the reason AC4 exists. `test_the_declared_budget_covers_the_measured_cost` asserts `baseline >= 250.0` against the LIVE config, a constant chosen in 2026-07 against the then-measured ~317s peak. It therefore only permits the baseline to move UP. Re-declaring it to the currently measured 212s - which is what the field is for, and which makes the instrument tighter rather than looser - is refused by the guard that exists to keep the baseline honest. Derive the floor from the recorded series rather than pinning a literal, or the guard goes stale in exactly the way it was written to prevent.

## Acceptance Criteria

- [ ] **AC1** Given a declared full-suite budget and a recorded full-suite series, when the budget lane reports, then it compares the latest full-suite total against that figure
- [ ] **AC2** Given no declared full-suite budget, when it reports, then it stays silent about the full suite rather than inventing a default
- [ ] **AC3** Given a per-commit series whose latest row is an outlier well above its neighbours, when the lane reports drift, then it does not read that single row as a regression
- [ ] **AC4** Given a repository whose measured gate cost has FALLEN since its baseline was declared, when the staleness guard runs, then it accepts the re-declared lower baseline and still refuses one that no longer reflects any recorded run

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-18 | sdlc-studio | Filed |
| 2026-08-18 | sdlc-studio | AC4 added: the staleness guard pins a literal floor and refuses a legitimate downward re-baseline |
