# US0081: Batch scaffold wiring polish

> **Status:** Done
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
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_artifact.py -k "batch_wires or batch_creates_wires or batch_defaults_to_the_lean_template"
- **Verified:** yes (2026-07-10)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-06 | sdlc | Created via `new` (deterministic) |
| 2026-09-27 | Claude Opus 5.5 | BG0805: AC1's -k term `batch_defaults_to_full_template`, which selected nothing, repointed to `batch_defaults_to_the_lean_template`, the rename BG0755 (18ea7f87) made when batch's default became the lean shape; it still asserts a full-template request renders the full body. The header-matches-the-template claim is carried by `test_batch_creates_wires_and_keeps_drift_zero` since BG0773. |
