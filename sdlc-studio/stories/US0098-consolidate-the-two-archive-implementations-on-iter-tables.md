# US0098: Consolidate the two archive implementations on iter_tables

> **Status:** Ready
> **Created:** 2026-07-09
> **Created-by:** sdlc-studio new
> **Epic:** EP0021
> **Persona:** Engineering seat
> **Affects:** scripts/archive.py, scripts/reconcile.py, scripts/tests/test_archive.py

## User Story

**As a** maintainer of the skill's tooling
**I want** one archive implementation built on `sdlc_md.iter_tables`, not two hand-rolled table walkers
**So that** a multi-view index cannot double-archive a row and a terminal-set mis-classification (BG0061) cannot recur

Delivers CR0182. Behaviour-preserving consolidation onto the declared structural boundary.

## Acceptance Criteria

### AC1: One archiver (or a documented thin-wrapper delegation)

- **Given** `archive.py` and `reconcile.py`'s archive paths
- **When** the code is inspected
- **Then** there is one archive implementation; the other delegates to it (a thin wrapper) or is removed
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_archive.py::SingleArchiverTests

### AC2: A multi-view index archives each terminal row exactly once

- **Given** a story index with multiple views (a Total table plus per-epic sub-tables)
- **When** archival runs
- **Then** each terminal row is archived exactly once with aligned columns (the current double-archive path is closed)
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_archive.py::MultiViewNoDoubleArchiveTests

### AC3: Both paths use the shared terminal-status source

- **Given** the consolidated archiver
- **When** it decides which rows are terminal
- **Then** it uses `sdlc_md.terminal_statuses`, so BG0061's Deferred mis-classification cannot recur
- **Verify:** grep -E "terminal_statuses" .claude/skills/sdlc-studio/scripts/archive.py

### AC4: No hand-rolled table walkers remain in the archive paths

- **Given** `archive.py` and `reconcile.py`'s archive paths
- **When** the code is inspected
- **Then** table parsing flows through `sdlc_md.iter_tables`; no private line-by-line table walker remains in either archive path
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_archive.py::IterTablesOnlyTests

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-09 | claude | Created via `new` (deterministic) |
| 2026-07-09 | claude | Groomed from CR0182 |
