# US0346: update tests, reference-scripts.md and CHANGELOG

> **Status:** Ready
> **Delivers:** CR0254
> **Created:** 2026-07-23
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Epic:** EP0116
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/tests/test_audit.py, .claude/skills/sdlc-studio/reference-scripts.md, CHANGELOG.md

## User Story

**As a** {{role}}
**I want** {{capability}}
**So that** {{benefit}}

## Acceptance Criteria

### AC1: the test modules are renamed with their subjects

- **Given** test files named for the old modules
- **When** the suite is discovered
- **Then** the tests live in `test_readiness.py` and `test_schema_check.py`, every one of them passes, and no test file references the old module names
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_readiness.py::RenameDocsTests::test_the_suites_are_renamed_and_green

### AC2: reference-scripts.md and CHANGELOG record the rename

- **Given** the scripts catalogue and the changelog
- **When** a reader looks up either script
- **Then** reference-scripts.md lists `readiness.py` and `schema_check.py` with no stale entry for the old names, and CHANGELOG's [Unreleased] carries the rename - an internal rename still changes what an agent reaches for
- **Verify:** grep readiness.py .claude/skills/sdlc-studio/reference-scripts.md

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-23 | sdlc-studio | Created via `new` (deterministic) |
