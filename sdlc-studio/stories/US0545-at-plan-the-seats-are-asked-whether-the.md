# US0545: At plan, the seats are asked whether the chosen content will deliver the goal, and a partial or no answer must name what is missing

> **Status:** Review
> **Delivers:** CR0470
> **Created:** 2026-07-28
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py
> **Epic:** EP0186
> **Points:** 5
> **Persona:** Maya Okafor

## User Story

**As a** an operator approving a plan
**I want** the seats asked whether the chosen content will deliver the goal, naming anything missing
**So that** the batch is checked against the goal before the work starts, not after

## Acceptance Criteria

### AC1: the plan asks whether the content delivers the goal

- **Given** a resolved batch and a stated goal
- **When** the seats are asked at plan time
- **Then** the question is whether these units deliver this goal, and a partial or no answer that names nothing missing is refused
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::GoalContentReviewTests::test_an_unexplained_partial_is_refused
- **Verified:** yes (2026-07-28)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-28 | sdlc-studio | Created via `new` (deterministic) |
| 2026-07-28 | Claude Opus 5 | Groomed: criteria authored against this story's slice, each with an executable Verify line |
