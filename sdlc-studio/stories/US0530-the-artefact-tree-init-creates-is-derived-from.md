# US0530: The artefact tree init creates is derived from the shipped type list, so a new type is never silently omitted

> **Status:** Ready
> **Delivers:** CR0457
> **Created:** 2026-07-28
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/init.py, .claude/skills/sdlc-studio/scripts/tests/test_init.py
> **Epic:** EP0180
> **Points:** 3
> **Persona:** Maya Okafor

## User Story

**As a** maintainer adding a new artefact type
**I want** the tree init creates derived from the shipped type list
**So that** a new type is never silently omitted from a new project, as the issue type was

## Acceptance Criteria

### AC1: the created tree covers every shipped artefact type

- **Given** the shipped list of artefact types
- **When** init runs on an empty project
- **Then** every type in that list has its directory and index, derived from the list rather than from a set typed into init
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_init.py::IssueTypeTests::test_every_shipped_type_gets_a_directory

### AC2: a type added to the shipped list is covered without editing init

- **Given** a type appended to the shipped list
- **When** init runs with no change to init
- **Then** the new type's directory and index are created, so the omission that made the issue type unusable cannot recur
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_init.py::IssueTypeTests::test_a_new_type_is_covered_without_editing_init

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-28 | sdlc-studio | Created via `new` (deterministic) |
| 2026-07-28 | Claude Fable 5 | Groomed against the carried lessons |
