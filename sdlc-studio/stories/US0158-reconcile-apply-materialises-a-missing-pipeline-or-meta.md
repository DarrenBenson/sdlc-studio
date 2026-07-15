# US0158: reconcile apply materialises a missing pipeline or meta index from its template, clearing missing-index drift

> **Status:** Done
> **Created:** 2026-07-15
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/reconcile.py
> **Epic:** EP0043
> **Points:** 5

## User Story

**As an** operator
**I want** reconcile to CREATE a missing index, not just detect it
**So that** a missing-index drift is fixable mechanically, not hand-authored.

## Acceptance Criteria

### AC1: apply creates a missing pipeline/meta index from template, populates it, clears drift; dry-run writes nothing

- **Given** a project with artefacts but a missing index (pipeline or the reviews/retros meta index)
- **When** `reconcile apply` runs (and dry-run)
- **Then** dry-run reports would-create and writes nothing; apply creates the index from the template, appends the census rows, and a subsequent detect is clean; an empty type is not seeded a phantom index
- **Verify:** shell cd .claude/skills/sdlc-studio/scripts && python3 -m unittest tests.test_reconcile.MissingIndexCreationTests
- **Verified:** yes (2026-07-16)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-15 | sdlc-studio | Created via `new` (deterministic) |
