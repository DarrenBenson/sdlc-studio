# US0028: decompose apply_type

> **Status:** Done
> **Epic:** [EP0005: Quality & Drift Control](../epics/EP0005-quality-drift.md)
> **Owner:** Autosprint (CR0030)
> **Reviewer:** --
> **Created:** 2026-06-20
> **GitHub Issue:** --

## User Story

**As a** maintainer
**I want** `reconcile.apply_type` decomposed so its cognitive complexity drops from 56
**So that** the repo's top hotspot - flagged by our own complexity tool (RFC0009) - is
easy to change, demonstrating the refactor-first loop end to end. Behaviour unchanged.

## Acceptance Criteria

### AC1: Behaviour preserved

- **Given** the decomposed apply_type + extracted helpers
- **When** the full reconcile suite runs (incl. the CR0026 corruption-guards)
- **Then** every test passes (the apply is byte-for-byte equivalent)
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_reconcile.py
- **Verified:** yes (2026-06-20)

### AC2: Complexity reduced and guarded

- **Given** the refactored apply_type
- **When** its cognitive complexity is measured
- **Then** it is below 15 (was 56), and a regression test guards it from regrowing
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_reconcile.py::RefactorGuardTests::test_apply_type_stays_decomposed
- **Verified:** yes (2026-06-20)

### AC3: Ragged-row no-op covered

- **Given** an index data row shorter than the Status column
- **When** apply runs
- **Then** it is a no-op, not a crash
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_reconcile.py::ApplyTests::test_apply_ignores_row_shorter_than_status_col
- **Verified:** yes (2026-06-20)

## Implementation

`scripts/reconcile.py`: extract `_plan_status_fixes`, `_row_id`, `_summary_cell_rewrite`,
`_data_row_rewrite`, `_header_kind`, `_rewrite_index_lines`; `apply_type` becomes a thin
orchestrator (cognitive 56 -> 7). Regression guard in `RefactorGuardTests`.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-06-20 | Autosprint (CR0030) | Decomposed from CR0030; critic APPROVE (behaviourally identical) |
