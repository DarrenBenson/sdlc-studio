# US0529: init creates the issues directory and its index, so the issue type is usable on a new project

> **Status:** Ready
> **Delivers:** CR0457
> **Created:** 2026-07-28
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/init.py, .claude/skills/sdlc-studio/scripts/tests/test_init.py
> **Epic:** EP0180
> **Points:** 2
> **Persona:** Maya Okafor

## User Story

**As a** operator starting a project and trying to file an issue
**I want** init to create the issues directory and its index
**So that** the issue type is usable on a new project rather than needing a directory made by hand

## Acceptance Criteria

### AC1: init creates the issues directory and a valid index

- **Given** an empty project
- **When** init runs
- **Then** the issues directory and its index exist and an issue can be filed immediately, with no hand-made directory
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_init.py::IssueTypeTests::test_init_creates_a_usable_issues_directory

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-28 | sdlc-studio | Created via `new` (deterministic) |
| 2026-07-28 | Claude Fable 5 | Groomed against the carried lessons |
