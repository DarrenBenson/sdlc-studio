# US0590: The doctrine states the content-versus-tooling line and names reference-scripts.md as the pre-task catalogue

> **Status:** Draft
> **Delivers:** CR0515
> **Created:** 2026-08-01
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/reference-doctrine.md, .claude/skills/sdlc-studio/reference-scripts.md
> **Epic:** EP0196
> **Points:** 2

## User Story

**As a** maintainer of a project that installs this skill
**I want** the content-versus-tooling line stated in the doctrine
**So that** a consuming project inherits the habit and not only the observation

## Acceptance Criteria

### AC1: the doctrine draws the content-versus-tooling line

- **Given** `reference-doctrine.md` as shipped
- **When** it is read
- **Then** it states that an agent authors content - prose, findings, criteria, rationale - and never tooling, and that a missing tool is a gap to file rather than a script to write
- **Verify:** pytest tools/tests/test_doctrine_tooling.py::DoctrineTests::test_the_content_tooling_line_is_stated

### AC2: the catalogue is named as the pre-task step

- **Given** the same document and `reference-scripts.md`
- **When** an agent is about to perform a mechanical task
- **Then** the doctrine names the catalogue as the thing to consult first, so a consuming project inherits the habit and not only the observation
- **Verify:** pytest tools/tests/test_doctrine_tooling.py::DoctrineTests::test_the_catalogue_is_named_as_the_first_step

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-01 | sdlc-studio | Created via `new` (deterministic) |
