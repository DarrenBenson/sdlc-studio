# US0078: Consolidate the two archive implementations on iter_tables

> **Status:** Draft
> **Created:** 2026-07-06
> **Created-by:** sdlc-studio new
> **Epic:** EP0018
> **Persona:** Skill Maintainer
> **Source:** CR-0182

## User Story

**As a** skill maintainer
**I want** the two archive implementations consolidated onto sdlc_md.iter_tables
**So that** they cannot disagree on terminal sets or double-archive a multi-view index

## Acceptance Criteria

### AC1: One archiver, per-table headers

- **Given** a multi-view story index fixture
- **When** it is archived
- **Then** each terminal row moves exactly once with aligned columns (no double-archive), via one
  archiver built on iter_tables using sdlc_md.terminal_statuses
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_archive.py -k consolidated

### AC2: No hand-rolled walkers remain

- **Given** the archive paths
- **When** the code is inspected
- **Then** no bespoke table walker remains in archive.py/reconcile.py archive paths
- **Verify:** grep .claude/skills/sdlc-studio/scripts/archive.py "iter_tables"

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-06 | sdlc | Created via `new` (deterministic) |
