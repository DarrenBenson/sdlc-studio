# CR-0606: A lane return records the builder's own token and minute totals, and the estimates ratio is withheld while delegated spend is unmeasured

> **Status:** Complete
> **Decomposed-into:** EP0271
> **Priority:** Medium
> **Type:** Improvement
> **Size:** S
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/sprint_report.py, .claude/skills/sdlc-studio/scripts/tests/test_lean_lane_delegated_tokens.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py
> **Date:** 2026-10-02
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-10-02T07:27:59Z

## Summary

RPT0014 reports tokens 2,350,747 against a forecast of 11,467,105 (0.2x) from the orchestrator session's meter alone; every builder and reviewer agent's spend, most of the run's, is NOT MEASURED, though each agent's total is reported to the orchestrator when it finishes. The ratio reads as an 80% saving that did not happen.

## Impact

Maya and the operator read a token figure off by several times, and the next plan's calibration learns from it.

## Acceptance Criteria

- [ ] Given `sprint lane return --units X --tokens 250000 --minutes 40`, when the page is derived, then X's tokens and minutes read 250,000 and 40 tagged as agent totals and the run's delegated total includes them; and given a run with no delegated total supplied, the Estimates tokens ratio cell reads withheld - delegated spend not measured rather than a number. Fails on: the current code has no --tokens on lane return and prints 0.2x
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_lane_delegated_tokens.py::LaneDelegatedTokensTests::test_a_lane_return_records_agent_totals_and_the_ratio_is_withheld_without_them

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-02 | sdlc-studio | Raised |
