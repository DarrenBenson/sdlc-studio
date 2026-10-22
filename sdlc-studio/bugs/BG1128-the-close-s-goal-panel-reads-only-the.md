# BG1128: The close's goal panel reads only the latest goal-review round, while the plan now reads every round on the latest wording, so after an owing seat records alone the two disagree on which seats have answered

> **Status:** Open
> **Severity:** Low
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_goal_review_one_round.py, changelog.d/BG1128.md, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py
> **Evidence:** US1096 repair round 1, outside-the-unit note, 2026-10-22.
> **Created:** 2026-10-22
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-10-22T16:09:50Z

## Summary

US1096's repair (2026-10-22) made `goal_review_status` read the rounds on the latest wording together, each seat's newest verdict back to the amendment that introduced the wording, so a seat owing a verdict can record it alone. The close's goal panel (`_recorded_goal_seats`, `_recorded_clause_verdicts` in sprint.py) still reads only the latest round: after an owing seat records alone, the plan sees every seat answered and the close sees only that one seat's verdict.

## Steps to Reproduce

Amend a goal with one seat asking to re-review; record that seat's verdict alone; compare the plan's goal status with the close's goal panel.

## Proposed Fix

Read the close's goal panel through the same rounds-on-the-latest-wording view `goal_review_status` uses.

## Acceptance Criteria

- [ ] **AC1** Given a goal amended with one seat asking to re-review and that seat's verdict recorded alone, when the close's goal panel is read, then it names every seat's verdict on the latest wording, as the plan does
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_goal_review_one_round.py::ClosePanelRoundsTests::test_the_close_panel_reads_every_round_on_the_latest_wording

## Impact

The close's goal judgement under-counts the seats that judged the goal it closes on.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-22 | Claude Opus 5.5 | Filed |
