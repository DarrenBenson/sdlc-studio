# US0023: reconcile apply - mechanical index fixes

> **Status:** Done
> **Epic:** [EP0005: Quality & Drift Control](../epics/EP0005-quality-drift.md)
> **Owner:** Autosprint (CR0026, rfc0003-apply)
> **Reviewer:** --
> **Created:** 2026-06-20
> **GitHub Issue:** --

## User Story

**As an** operator
**I want** `reconcile apply` to perform the mechanical index fixes deterministically
**So that** drift correction is a tested, idempotent script step instead of ~3-4k
tokens of re-derived prose (RFC0003 / CR0026).

## Context

Delivers RFC0003 (scoped). `reconcile apply [--scope] [--dry-run]` rewrites each
drifted index row's Status cell (positionally, by header) to the file's canonical
status and recomputes the summary counts; idempotent; `--dry-run` reports without
writing. Structural classes (missing-row/orphan-row/missing-index) stay report-only.
Also hardened `_table_cells` to respect escaped pipes (`\|` in a cell) so apply is
write-safe - this dropped consuming repo A's stories drift 6 -> 1.

## Acceptance Criteria

### AC1: Fixes status cells + recomputes counts

- **Given** an index row whose Status drifts from its file, and stale summary counts
- **When** `apply_type` runs
- **Then** the row's Status is set to the file's status, the counts are recomputed, and `detect` then shows no status-mismatch or count-mismatch
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_reconcile.py::ApplyTests::test_apply_fixes_status_and_counts_idempotent
- **Verified:** yes (2026-06-20)

### AC2: --dry-run writes nothing

- **Given** drift
- **When** `apply_type(dry_run=True)` runs
- **Then** it reports the changes but the index file is byte-unchanged
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_reconcile.py::ApplyTests::test_apply_dry_run_writes_nothing
- **Verified:** yes (2026-06-20)

### AC3: Structural classes left report-only

- **Given** a missing-row and an orphan-row
- **When** apply runs
- **Then** they are not changed; `detect` still reports them
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_reconcile.py::ApplyTests::test_apply_leaves_structural_classes
- **Verified:** yes (2026-06-20)

### AC4: Escaped pipes parsed safely

- **Given** an index row whose cell contains `\|`
- **When** `_table_cells` parses it
- **Then** the columns are not shifted (apply writes the right cell)
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_reconcile.py::IndexParseTests::test_table_cells_respects_escaped_pipe
- **Verified:** yes (2026-06-20)

## Implementation

`scripts/reconcile.py`: `apply_type` / `_row_counts` / `cmd_apply` + `apply`
subcommand; `_table_cells` splits on unescaped pipes. Doc in `reference-reconcile.md`.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-06-20 | Autosprint (CR0026) | Decomposed from CR0026 / RFC0003 |
