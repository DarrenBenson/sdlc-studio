# US0081: Batch scaffold wiring polish

> **Status:** Draft
> **Created:** 2026-07-06
> **Created-by:** sdlc-studio new
> **Epic:** EP0018
> **Persona:** Skill Maintainer
> **Source:** CR-0166

## User Story

**As a** skill maintainer
**I want** the batch scaffold wiring edges cleaned up
**So that** a fresh greenfield chain produces tidy artefacts an agent does not hand-fix

## Acceptance Criteria

### AC1: Clean epic wiring and story header

- **Given** a two-epic four-story batch
- **When** it scaffolds
- **Then** epic wiring replaces the placeholder (no stray separator), the full-template story header
  matches templates/core/story.md, and the empty Stories-by-Epic table is populated or omitted
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_artifact.py -k batch_wiring

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-06 | sdlc | Created via `new` (deterministic) |
