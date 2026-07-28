# US0547: Both answers are recorded on the run and shown side by side, reporting a prediction miss where the plan predicted delivery and the close judged otherwise

> **Status:** Done
> **Delivers:** CR0470
> **Created:** 2026-07-28
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py
> **Epic:** EP0186
> **Points:** 3
> **Persona:** Maya Okafor

## User Story

**As a** an operator calibrating how seriously plan-time answers are given
**I want** both goal answers recorded and shown side by side, with a prediction miss reported
**So that** over several sprints I can see whether the plan-time question is being answered seriously

## Acceptance Criteria

### AC1: a prediction miss is reported

- **Given** a run whose plan predicted the content would deliver the goal
- **When** the close judges it was not achieved
- **Then** both answers are shown side by side and the difference is reported as a prediction miss
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::GoalContentReviewTests::test_a_prediction_miss_is_reported
- **Verified:** yes (2026-07-28)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-28 | sdlc-studio | Created via `new` (deterministic) |
| 2026-07-28 | Claude Opus 5 | Groomed: criteria authored against this story's slice, each with an executable Verify line |
