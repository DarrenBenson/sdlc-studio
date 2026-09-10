# BG0608: The budget line still LEADS with the seconds comparison BG0594 proved uninformative, so the reader's eye lands on +130% and the real verdict sits in the last bracket

> **Status:** Fixed
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

- [ ] **AC5** Given a run whose test count IS recorded, when the line is composed, then it does NOT say the width is unrecorded and names the width beside its total. AC4's paired control: a note appended unconditionally satisfies AC4 while telling every reader the width is unknown on the lines that carry it
  - **Verify:** pytest tools/tests/test_gate_timing.py::BudgetLineTests::test_the_note_is_withheld_when_a_count_is_recorded
- [ ] **AC6** Given the drift clause is withheld, when the line is composed, then it names the config key that restores the figure, chosen for the series it is on. Both sibling disclosures in the same line name theirs, and BG0594 AC5 made that law for the neighbouring clause - a reader who has just lost the trend needs the route back from the line in front of them
  - **Verify:** pytest tools/tests/test_gate_timing.py::BudgetLineTests::test_the_withheld_clause_names_the_key_that_restores_the_figure
- [ ] **AC7** Given a rate clause, when the line is composed, then it names the width the rate was taken over. This unit's whole premise is that a total is selection width times cost-per-test, and the leading clause is the one a commit message quotes
  - **Verify:** pytest tools/tests/test_gate_timing.py::BudgetLineTests::test_the_leading_clause_names_the_width_the_rate_was_taken_over
- [ ] **AC8** Given a selected run with a baseline declared and NO current test count recorded, when the drift clause is withheld, then it says this side's width is unrecorded rather than printing a bare number. The clause compares this width against the baseline's, so an unknown on this side has to be said
  - **Verify:** pytest tools/tests/test_gate_timing.py::BudgetLineTests::test_an_unrecorded_current_width_is_named_in_the_withheld_clause
- [ ] **AC9** Given a non-numeric `gate_budget.baseline_tests`, when the line is composed, then the report degrades to the withheld clause rather than raising. `budget_config` states that a bad config is advisory here and never a commit failure, and the hook swallows this command's stderr - so an unguarded read takes the whole budget line down with no diagnostic
  - **Verify:** pytest tools/tests/test_gate_timing.py::BudgetLineTests::test_a_non_numeric_baseline_width_degrades_to_silence
- [ ] **AC10** Given a FULL run judged against the per-commit ceiling because no `gate_budget.full_seconds` is declared, when the line is composed, then the drift percentage is withheld on the same rule as a selected run. That limb compares a whole-suite total with the per-commit baseline - measured at +184% for a 7,400-test run against a ~1,400-test one - which is the cross-population figure this unit exists to remove
  - **Verify:** pytest tools/tests/test_gate_timing.py::BudgetLineTests::test_a_full_run_judged_on_the_per_commit_baseline_withholds_the_percentage
- [ ] **AC11** Given a FULL run judged on its OWN series, when the line is composed, then the percentage is still stated. The paired control for AC10: two whole-suite totals are like-for-like even with neither count recorded, and withholding there would remove the trend from the only comparison that never needed a width
  - **Verify:** pytest tools/tests/test_gate_timing.py::BudgetLineTests::test_a_full_run_on_its_own_series_keeps_its_percentage

- [ ] **AC12** Given a run over its rate ceiling, when `gate_timing.py budget` PRINTS its line, then the verdict word appears once. The stutter lives in the command rather than in the report, so every criterion above - each reading `budget_report` - is blind to it, which is what the repo's own lane-check named
  - **Verify:** pytest tools/tests/test_gate_timing.py::BudgetLineTests::test_the_shipped_command_prints_the_verdict_word_once
- [ ] **AC13** Given a run over a seconds budget with NO rate ceiling declared, when the same command prints, then it still says the run is over. The paired control: with no verdict word in the detail, the command's own prefix is the only thing that says so, and removing it to fix the stutter would take the verdict off the line
  - **Verify:** pytest tools/tests/test_gate_timing.py::BudgetLineTests::test_the_shipped_command_still_says_over_when_only_the_total_decides

## Test Plan

| Criterion | Mutant - the production change this test must fail on | Title |
| --- | --- | --- |
| AC1 | in tools/gate_timing.py, move the `rate verdict` concatenation back below the drift block, restoring the original append order | Given a run for which a per-test rate and a declared rate ceiling both exist, when `gate_timing.py budget` composes its line, then the FIRST clause is the rate verdict and it reads `under` for a run inside the ceiling. Today the line opens with a seconds total against a seconds budget and the rate verdict is appended last, so the figure a reader takes away is the one the tool does not judge on |
| AC2 | in tools/gate_timing.py, hard-code the word chosen from `over` to the literal `under` at the point the clause is built | Given a run whose per-test rate EXCEEDS the declared ceiling, when the same command runs, then that same leading clause reads `over` - the paired control against a clause hard-coded to reassure. Both halves are false at HEAD, because at HEAD neither run leads with a rate clause at all |
| AC3 | in tools/gate_timing.py, hoist the `baseline`/`when` block above the `series == "selected"` test so it runs unconditionally, dropping the width annotation | Given a SELECTED run and a baseline recorded at a different selection width, when the line is composed, then the drift clause either names both widths or is withheld, and never reports a bare percentage against a baseline taken at another width. This is the half that is false at HEAD: the baseline-and-drift clause is appended to a selected run with no width on either figure |
| AC4 | in tools/gate_timing.py, delete the `else` limb that annotates `detail` when `rate is None`, leaving the bare f-string | Given a run for which no test count is recorded AND no rate ceiling is declared, when the line is composed, then the seconds total it still prints says the width is unrecorded rather than standing bare. The narrower Given is the measured one: with a ceiling declared, HEAD already says a run recorded no test count from the limb below, so the wider wording passed before any code was written |

| AC5 | in tools/gate_timing.py, append the unrecorded-width note unconditionally, above the branch that decides it | Given a run whose test count IS recorded, when the line is composed, then it does NOT say the width is unrecorded and names the width beside its total |
| AC6 | in tools/gate_timing.py, delete the `Declare ... to restore it` sentence from the withheld clause | Given the drift clause is withheld, when the line is composed, then it names the config key that restores the figure, chosen for the series it is on |
| AC7 | in tools/gate_timing.py, delete `over {tests} tests` from the rate clause | Given a rate clause, when the line is composed, then it names the width the rate was taken over |
| AC8 | in tools/gate_timing.py, replace the `an unrecorded number of` arm with a literal | Given a selected run with a baseline declared and NO current test count recorded, when the drift clause is withheld, then it says this side's width is unrecorded rather than printing a bare number |
| AC9 | in tools/gate_timing.py, read the baseline width with a bare `float()`, unguarded | Given a non-numeric `gate_budget.baseline_tests`, when the line is composed, then the report degrades to the withheld clause rather than raising |
| AC10 | in tools/gate_timing.py, exempt every non-selected series from the withholding, as the first cut did | Given a FULL run judged against the per-commit ceiling because no `gate_budget.full_seconds` is declared, when the line is composed, then the drift percentage is withheld on the same rule as a selected run |
| AC11 | in tools/gate_timing.py, withhold the percentage on every series | Given a FULL run judged on its OWN series, when the line is composed, then the percentage is still stated |

| AC12 | in tools/gate_timing.py, prefix the command's own verdict word whenever the run is over budget | Given a run over its rate ceiling, when gate_timing.py budget PRINTS its line, then the verdict word appears once |
| AC13 | in tools/gate_timing.py, drop the command's prefix altogether | Given a run over a seconds budget with NO rate ceiling declared, when the same command prints, then it still says the run is over |

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-24 | sdlc-studio | Filed |
| 2026-09-09 | Claude Fable 5.1 | Delivered in 0418d963. Four mutants, four killed. The Proposed Fix's demand that `gate_budget.seconds` be re-declared is NOT delivered and was ruled at plan review round two: the criteria supersede it and the config file is out of `Affects`. Recorded here as well as on the repair record, because a reader of this artefact alone would otherwise see an undelivered demand and no ruling |
| 2026-09-09 | Claude Fable 5.1 | Delivery review, product seat: REJECT, and it was right. The changelog fragment claimed the percentage is stated `only when both widths are on record`, which is false for the FULL series - `elif base_tests or series != "selected"` never withholds there, so a full run prints the figure in the same sentence that admits the width is unknown. It also told the reader to declare `full_baseline_tests`, which restores nothing and is pinned by no criterion and no test. The fragment now says what the code does: withheld on a SELECTED run whose baseline records no width, kept on a full one. The withholding clause also names `gate_budget.baseline_tests` now, matching the two sibling disclosures in the same function, which both name the key that would settle them. Reported and not acted on: the fallback limb still compares a full total to the selected-series baseline, which is the same cross-width percentage one limb over, and the `OVER` printed by the command's own prefix is now repeated by the leading clause |
| 2026-09-09 | Claude Opus 5 | Round two, all three seats REJECT, and the findings converged on prose that execution refuted. The fragment claimed the percentage is stated only when both widths are on record; the code exempted EVERY non-selected series, so a full run judged against the per-commit ceiling printed a bare +184% - a 7,400-test total against a ~1,400-test baseline, the same cross-population figure this unit exists to remove, defended in a comment as like-for-like when that is true of one of the two shapes it covered. The carve-out is now the own-series full run alone (AC10, AC11). The line also printed its verdict twice, `OVER - rate ... - OVER - REGRESSION`, because the command prefixed a clause that already carried the word. Six further criteria pin what shipped unpinned: the withheld clause's key sentence, the rate clause's width, the unrecorded-current-width arm, the guarded read of a non-numeric width key, and AC4's missing paired control. Both width keys are now documented in `.config.yaml`, and the fragment's width window is re-measured from the live series (2,197 to 6,101) rather than a stale config comment |
