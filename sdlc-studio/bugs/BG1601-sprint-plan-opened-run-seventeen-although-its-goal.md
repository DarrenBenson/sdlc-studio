# BG1601: sprint plan opened run seventeen although its goal had no seat review, the recorded one being an earlier run's goal, and the close then refuses goal-seat-reviewed past its window

> **Status:** Open
> **Severity:** Low
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint_goal_review.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py, changelog.d/BG1601.md
> **Evidence:** sprint close --dry-run --retro RETRO0150, 2026-11-18: 'STOP checklist: goal-seat-reviewed: Sprint Goal stated and seat-reviewed BEFORE the plan - past its window'.
> **Created:** 2026-11-18
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-18T18:19:47Z

## Summary

Run seventeen (RUN-01M7QMZ0) was planned on the goal 'A reviewer reading only the front door knows SDLC Studio runs in their own harness, models and change process' while `sprint_goal_review` in run-state.json recorded a review of a different goal ('A sprint costs at most 1.5M priced tokens per point...'). The close checklist marks goal-seat-reviewed '(enforce at sprint plan)', but the plan printed advice and opened the run, so the gap surfaced only at the close, where it can no longer be answered and only a waiver clears it.

## Steps to Reproduce

Record a goal review for goal A, then run `sprint plan` with a different goal B: the run opens; `sprint close --dry-run` later refuses goal-seat-reviewed past its window.

## Proposed Fix

Have sprint plan refuse, or require an explicit recorded skip, when the recorded goal review is of a different goal than the one being planned, so the close never meets the gap past its window.

## Acceptance Criteria

- [ ] **AC1** The behaviour described is corrected: Run seventeen (RUN-01M7QMZ0) was planned on the goal 'A reviewer reading only the front door knows SDLC Studio runs in their own harness, models and change...
- [ ] **AC2** Following the recorded steps no longer reproduces the defect: Record a goal review for goal A, then run `sprint plan` with a different goal B: the run opens; `sprint close --dry-run` later refuses goal-seat-reviewed past...
- [ ] **AC3** The proposed fix lands, pinned by a test: Have sprint plan refuse, or require an explicit recorded skip, when the recorded goal review is of a different goal than the one being planned, so the close...

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-18 | sdlc-studio | Filed |
