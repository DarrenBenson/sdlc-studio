# US0592: The goal seat review is enforced by sprint plan --write, so skipping it is refused where it can still be run

> **Status:** Draft
> **Delivers:** CR0513
> **Created:** 2026-08-01
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py
> **Epic:** EP0197
> **Points:** 5

## User Story

**As a** operator setting a sprint's direction
**I want** the goal seat review enforced at plan time
**So that** a seat can still refuse the goal while the batch can be re-cut

## Acceptance Criteria

### AC1: skipping the goal review is refused at plan time

- **Given** `sprint plan --write` invoked with no seat review of the Sprint Goal
- **When** the plan is written
- **Then** it is refused where the review can still be run, rather than surfacing at a close where the batch has already been delivered and re-cut
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::GoalReviewWindowTests::test_an_unreviewed_goal_refuses_the_plan

### AC2: the recorded escape names its authoriser at the moment it is taken

- **Given** an operator who deliberately skips the seat review
- **When** the plan is written with the recorded opt-out
- **Then** the waiver is recorded then and there with its authoriser, so the decision is made when it can still be reconsidered
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::GoalReviewWindowTests::test_the_escape_is_recorded_at_plan_time

### AC3: a reviewed goal plans without complaint

- **Given** a Sprint Goal carrying seat verdicts
- **When** the plan is written
- **Then** it succeeds silently - the control against a gate that refuses everything
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::GoalReviewWindowTests::test_a_reviewed_goal_plans_cleanly

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-01 | sdlc-studio | Created via `new` (deterministic) |
