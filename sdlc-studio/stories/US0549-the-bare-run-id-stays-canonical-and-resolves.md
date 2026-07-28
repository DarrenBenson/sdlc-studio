# US0549: The bare run id stays canonical and resolves the sprint whatever the slug says, so rewording a goal orphans nothing

> **Status:** Draft
> **Delivers:** CR0471
> **Created:** 2026-07-28
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/lib/run_state.py
> **Epic:** EP0187
> **Points:** 3
> **Persona:** Maya Okafor

## User Story

**As a** {{role}}
**I want** {{capability}}
**So that** {{benefit}}

## Acceptance Criteria

### AC1: the run id stays canonical across a reworded goal

- **Given** a sprint whose recorded goal no longer matches the slug in its filename
- **When** the sprint is resolved by its run id
- **Then** it resolves, so rewording a goal orphans no reference
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_run_state.py::SprintNamingTests::test_the_run_id_resolves_a_sprint_whose_slug_is_stale

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-28 | sdlc-studio | Created via `new` (deterministic) |
| 2026-07-28 | Claude Opus 5 | Groomed: criteria authored against this story's slice, each with an executable Verify line |
