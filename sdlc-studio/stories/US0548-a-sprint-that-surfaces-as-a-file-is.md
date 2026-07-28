# US0548: A sprint that surfaces as a file is named sprint-<run id>-<goal slug>, slugged by the shared helper

> **Status:** Draft
> **Delivers:** CR0471
> **Created:** 2026-07-28
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py
> **Epic:** EP0187
> **Points:** 3
> **Persona:** Maya Okafor

## User Story

**As a** {{role}}
**I want** {{capability}}
**So that** {{benefit}}

## Acceptance Criteria

### AC1: a sprint file is named for its goal

- **Given** a run with a recorded Sprint Goal
- **When** the sprint surfaces as a file
- **Then** it is named sprint-<run id>-<goal slug>, slugged by the shared helper the other artefact types use
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::SprintNamingTests::test_a_sprint_file_carries_its_goal_slug

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-28 | sdlc-studio | Created via `new` (deterministic) |
| 2026-07-28 | Claude Opus 5 | Groomed: criteria authored against this story's slice, each with an executable Verify line |
