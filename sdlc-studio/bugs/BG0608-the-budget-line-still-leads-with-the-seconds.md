# BG0608: The budget line still LEADS with the seconds comparison BG0594 proved uninformative, so the reader's eye lands on +130% and the real verdict sits in the last bracket

> **Status:** Open
> **Severity:** Medium
> **Points:** 2
> **Verification depth:** functional (authored at plan time as the tier this unit is driven to; the derived half is written by `verify_ac.py depth --write` at delivery, never by hand)
> **Affects:** tools/gate_timing.py, tools/tests/test_gate_timing.py
> **Evidence:** RUN-01M0JD1W, 2026-08-24. sdlc-studio/.local/gate-timings.json records `total.selected` at 206, 265, 205, 186, 174, 531, 738, 752, 751, 728 seconds against `total.selected.tests` of 1313, 1799, 1578, 1292, 1588, 5442, 5965, 6041, 6041, 5965. The step is in width, not in cost. This line has now twice been the thing that cost operator attention during a close.
> **Created:** 2026-08-24
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

BG0594 established that a seconds ceiling cannot describe a population whose width varies from 1,418 to 5,973 tests, and shipped `rate_seconds_per_test` as the quantity actually being budgeted. It did not change what the lane PRINTS. The line still opens with the seconds comparison and the percentage against a July baseline, and puts the rate verdict last, in brackets. A human reads the first clause. The signal BG0594 removed from the arithmetic is still the signal a person acts on, so the fix landed in the code and not in the report.

## Steps to Reproduce

Run `python3 tools/gate_timing.py budget` in this repository on 2026-08-24. It prints: `gate-budget: 728s of a 380s budget, 0.122s/test over 5965 tests [selected run] (baseline 317s on 2026-07-26, +130% since) [rate verdict: 0.122 vs 0.152s/test ceiling]`. The two figures disagree in direction - 92% over on seconds, 20% under on rate - and the one that is wrong by BG0594's own argument is read first. The recorded series shows why the seconds figure moved: selected width went from 1,313-1,799 tests in the first five recorded runs to 5,442-6,041 in the last five, so the total roughly quadrupled while the per-test cost stayed inside 0.10-0.13.

## Proposed Fix

Lead with the rate verdict and demote the seconds figure to context, or drop the percentage-since-baseline entirely for the selected series - a percentage against a baseline taken at a different selection width is a comparison of two different populations. State the width beside any total that is kept, so a reader cannot take a wide commit for a regression. `seconds: 380` should either be re-declared as a full-suite figure or removed for the selected series, since BG0594's own reasoning says one scalar cannot describe it.

## Acceptance Criteria

- [ ] **AC1** Given a run for which a per-test rate and a declared rate ceiling both exist, when `gate_timing.py budget` composes its line, then the FIRST clause is the rate verdict and it reads `under` for a run inside the ceiling. Today the line opens with a seconds total against a seconds budget and the rate verdict is appended last, so the figure a reader takes away is the one the tool does not judge on
  - **Verify:** pytest tools/tests/test_gate_timing.py::BudgetLineTests::test_the_line_leads_with_the_rate_verdict
  - **Verified:** yes (2026-09-08)
- [ ] **AC2** Given a run whose per-test rate EXCEEDS the declared ceiling, when the same command runs, then that same leading clause reads `over` - the paired control against a clause hard-coded to reassure. Both halves are false at HEAD, because at HEAD neither run leads with a rate clause at all
  - **Verify:** pytest tools/tests/test_gate_timing.py::BudgetLineTests::test_an_over_rate_run_reads_over_in_the_same_leading_clause
  - **Verified:** yes (2026-09-08)
- [ ] **AC3** Given a SELECTED run and a baseline recorded at a different selection width, when the line is composed, then the drift clause either names both widths or is withheld, and never reports a bare percentage against a baseline taken at another width. This is the half that is false at HEAD: the baseline-and-drift clause is appended to a selected run with no width on either figure
  - **Verify:** pytest tools/tests/test_gate_timing.py::BudgetLineTests::test_a_cross_width_drift_clause_names_both_widths_or_is_withheld
  - **Verified:** yes (2026-09-08)
- [ ] **AC4** Given a run for which no test count is recorded AND no rate ceiling is declared, when the line is composed, then the seconds total it still prints says the width is unrecorded rather than standing bare. The narrower Given is the measured one: with a ceiling declared, HEAD already says a run recorded no test count from the limb below, so the wider wording passed before any code was written
  - **Verify:** pytest tools/tests/test_gate_timing.py::BudgetLineTests::test_an_unmeasured_width_is_named_beside_its_total
  - **Verified:** yes (2026-09-08)

## Test Plan

| Criterion | Mutant - the production change this test must fail on | Title |
| --- | --- | --- |
| AC1 | in tools/gate_timing.py, move the `rate verdict` concatenation back below the drift block, restoring the original append order | Given a run for which a per-test rate and a declared rate ceiling both exist, when `gate_timing.py budget` composes its line, then the FIRST clause is the rate verdict and it reads `under` for a run inside the ceiling. Today the line opens with a seconds total against a seconds budget and the rate verdict is appended last, so the figure a reader takes away is the one the tool does not judge on |
| AC2 | in tools/gate_timing.py, hard-code the word chosen from `over` to the literal `under` at the point the clause is built | Given a run whose per-test rate EXCEEDS the declared ceiling, when the same command runs, then that same leading clause reads `over` - the paired control against a clause hard-coded to reassure. Both halves are false at HEAD, because at HEAD neither run leads with a rate clause at all |
| AC3 | in tools/gate_timing.py, hoist the `baseline`/`when` block above the `series == "selected"` test so it runs unconditionally, dropping the width annotation | Given a SELECTED run and a baseline recorded at a different selection width, when the line is composed, then the drift clause either names both widths or is withheld, and never reports a bare percentage against a baseline taken at another width. This is the half that is false at HEAD: the baseline-and-drift clause is appended to a selected run with no width on either figure |
| AC4 | in tools/gate_timing.py, delete the `else` limb that annotates `detail` when `rate is None`, leaving the bare f-string | Given a run for which no test count is recorded AND no rate ceiling is declared, when the line is composed, then the seconds total it still prints says the width is unrecorded rather than standing bare. The narrower Given is the measured one: with a ceiling declared, HEAD already says a run recorded no test count from the limb below, so the wider wording passed before any code was written |

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-24 | sdlc-studio | Filed |
