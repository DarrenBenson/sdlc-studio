# US0550: A run with no goal recorded falls back to the id alone rather than inventing a slug

> **Status:** Review
> **Delivers:** CR0471
> **Created:** 2026-07-28
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py
> **Epic:** EP0187
> **Points:** 2
> **Persona:** Maya Okafor

## User Story

**As a** an operator running a sprint before its goal is set
**I want** a run with no recorded goal named by its id alone
**So that** the tool does not invent a slug for a goal nobody has written

## Acceptance Criteria

### AC1: a goalless run falls back to the id

- **Given** a run with no goal recorded
- **When** its name is derived
- **Then** it is the bare run id rather than an invented slug
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::SprintNamingTests::test_a_run_with_no_goal_is_named_by_id_alone
- **Verified:** yes (2026-07-28)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-28 | sdlc-studio | Created via `new` (deterministic) |
| 2026-07-28 | Claude Opus 5 | Groomed: criteria authored against this story's slice, each with an executable Verify line |
