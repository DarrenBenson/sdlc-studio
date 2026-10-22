# BG1126: A seat-requested amendment of an open run's goal leaves the run state on the old goal, so the close's goal read reports 'a different goal'

> **Status:** Open
> **Severity:** Low
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_goal_review_one_round.py, changelog.d/BG1126.md, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py
> **Evidence:** US1096 QA review round 1, qa-seat-US1096-r1, at 7f113429: pre-existing finding, reproduced at e877a6b9.
> **Created:** 2026-10-22
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-10-22T15:07:16Z

## Summary

US1096's QA review (round 1, 2026-10-22), pre-existing at e877a6b9. US1096 moves an open run's goal only for an amendment recorded with `--requested-by operator`. An amendment recorded with `--requesting-seat <role>` on an open run records the new wording on the goal-review round but leaves the run state's `sprint_goal` on the planned wording, so the close's goal read compares against the old goal and reports the reviewed one as a different goal.

## Steps to Reproduce

Open a run with goal G; record `sprint.py goal-review record --goal G2 --amend-from G --requesting-seat qa ...`; run the close's goal read: it judges G and names G2 as different.

## Proposed Fix

Apply US1096's open-run move to a seat-requested amendment too (same guards: the open run's goal, no goal verdict yet, the word limit), or refuse a seat-requested amendment on an open run and point to `--requested-by operator`.

## Acceptance Criteria

- [ ] **AC1** Given an open run with goal G and a seat-requested amendment to G2, when the close's goal is read, then it judges G2, or the amendment was refused naming --requested-by operator
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_goal_review_one_round.py::SeatAmendOpenRunTests::test_a_seat_requested_amendment_does_not_leave_the_run_on_the_old_goal

## Impact

A goal improved at a seat's request mid-run is judged at the close against the wording it replaced.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-22 | Claude Opus 5.5 | Filed |
