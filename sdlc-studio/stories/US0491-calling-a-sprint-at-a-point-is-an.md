# US0491: Calling a sprint at a point is an honest close: the unstarted remainder is descoped with a reason and returns to the backlog

> **Status:** Ready
> **Delivers:** RFC0057
> **Created:** 2026-07-27
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py
> **Epic:** EP0176
> **Points:** 5

## User Story

**As a** operator whose sprint met reality two thirds of the way through
**I want** to call the sprint at that point and have the close record what was achieved
**So that** a sprint that delivered most of its batch records that, instead of being abandoned as though it delivered nothing

## Acceptance Criteria

### AC1: calling the sprint closes it honestly against the goal

- **Given** an open run with delivered and unstarted units
- **When** the sprint is called at that point
- **Then** the close records what was delivered against the Sprint Goal and completes the close paperwork, rather than abandoning the run as stop does
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::CallItHereTests::test_calling_the_sprint_closes_it_against_the_goal

### AC2: the descoped remainder carries a reason

- **Given** unstarted units in the batch
- **When** the sprint is called with no reason given
- **Then** it is refused until a reason is supplied, matching the reason batch drop already requires, so a descope is never unexplained
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::CallItHereTests::test_a_descope_without_a_reason_is_refused

### AC3: descoped units return to the backlog rather than being carried

- **Given** a called sprint with a descoped remainder
- **When** the close completes
- **Then** each descoped unit is back in the backlog at its prior status and none is attached to a following charter, so no coupling between sprints is created
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::CallItHereTests::test_descoped_units_return_to_the_backlog_uncoupled

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-27 | sdlc-studio | Created via `new` (deterministic) |
| 2026-07-27 | Claude Fable 5 | Groomed against the D0072 rulings |
