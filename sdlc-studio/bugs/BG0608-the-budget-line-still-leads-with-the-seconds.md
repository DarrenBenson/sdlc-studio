# BG0608: The budget line still LEADS with the seconds comparison BG0594 proved uninformative, so the reader's eye lands on +130% and the real verdict sits in the last bracket

> **Status:** Open
> **Severity:** Medium
> **Points:** 2
> **Affects:** tools/gate_timing.py, tools/tests/test_gate_timing.py, sdlc-studio/.config.yaml
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

- [ ] **AC1** Given a selected run whose per-test rate is inside the declared rate ceiling, when `gate_timing.py budget` prints its line, then the first clause states the rate verdict and the word describing the run's standing is `under`, not a seconds overage
- [ ] **AC2** Given a selected run whose per-test rate EXCEEDS the rate ceiling, when the same command runs, then the first clause reports it over - the paired control, so demoting the seconds figure is not the same as never flagging anything
- [ ] **AC3** Given two runs at the same per-test rate and different selection widths, when both are reported, then they reach the same verdict, and neither is described as a percentage change against a baseline taken at a third width
- [ ] **AC4** Given any total in seconds that is still printed, when it appears, then the selection width it was measured over appears beside it in the same clause

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-24 | sdlc-studio | Filed |
