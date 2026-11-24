# BG1601: sprint plan opened run seventeen although its goal had no seat review, the recorded one being an earlier run's goal, and the close then refuses goal-seat-reviewed past its window

> **Status:** Closed
> **Severity:** Low
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint_goal_review.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py, changelog.d/BG1601.md
> **Evidence:** sprint close --dry-run --retro RETRO0150, 2026-11-18: 'STOP checklist: goal-seat-reviewed: Sprint Goal stated and seat-reviewed BEFORE the plan - past its window'.
> **Created:** 2026-11-18
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-18T18:19:47Z
> **Closed because:** OBSOLETE, re-checked at cecc9dfe7 for run twenty-five by the qa seat (Sam Eriksson). The close half was fixed by 74436b8b3: since then the close's dry run shows a past-window goal-seat-reviewed row as "note checklist, reported not blocking", and the real close has never been held by it since a65f0a4af. The plan half is shipped design: the seat review advises and a missing review must not refuse the plan, pinned by test_lean_goal.py::GoalSeatReadTests::test_a_missing_seat_read_is_recorded_as_not_read, so the filed fix would break it. The plan today prints "the Sprint Goal went UNREVIEWED - the recorded review is of a different goal".

## Summary

Run seventeen (RUN-01M7QMZ0) was planned on the goal 'A reviewer reading only the front door knows SDLC Studio runs in their own harness, models and change process' while `sprint_goal_review` in run-state.json recorded a review of a different goal ('A sprint costs at most 1.5M priced tokens per point...'). The close checklist marks goal-seat-reviewed '(enforce at sprint plan)', but the plan printed advice and opened the run, so the gap surfaced only at the close, where it can no longer be answered and only a waiver clears it.

## Steps to Reproduce

Record a goal review for goal A, then run `sprint plan` with a different goal B: the run opens; `sprint close --dry-run` later refuses goal-seat-reviewed past its window.

## Proposed Fix

Have sprint plan refuse, or require an explicit recorded skip, when the recorded goal review is of a different goal than the one being planned, so the close never meets the gap past its window.

## Acceptance Criteria

Re-checked for run twenty-five as obsolete; the two criteria below are the re-check, each run against HEAD.

- [x] **AC1** Given a run whose recorded goal-seat review falls outside its window, when the close checklist is read, then goal-seat-reviewed is reported as expired, not outstanding, so the close is not held by it (the close half, fixed by 74436b8b3).
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py::ChecklistWindowTests::test_an_expired_item_reports_rather_than_gates
  - **Verified:** yes (2026-11-24)
- [x] **AC2** Given a plan whose goal no seat has read, when `sprint plan` runs, then the missing read is recorded as not read and the plan is not refused: the seat review advises by design, so the filed fix (refuse the plan) is not wanted.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_goal.py::GoalSeatReadTests::test_a_missing_seat_read_is_recorded_as_not_read
  - **Verified:** yes (2026-11-24)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-18 | sdlc-studio | Filed |
| 2026-11-24 | Sam Eriksson (qa) | Re-checked for run twenty-five: obsolete. The close half was fixed by 74436b8b3, and the plan half is the advisory design a test pins; closed |
