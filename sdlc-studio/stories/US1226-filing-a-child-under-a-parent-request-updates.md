# US1226: Filing a child under a parent request updates the parent's spawned work cell in the same write

> **Status:** Draft
> **Risk-class:** elevated
> **Delivers:** CR0683
> **Created:** 2026-11-17
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/file_finding.py, .claude/skills/sdlc-studio/scripts/artifact.py, .claude/skills/sdlc-studio/scripts/tests/test_file_finding.py, .claude/skills/sdlc-studio/scripts/tests/test_artifact.py
> **Epic:** EP0334
> **Points:** 2
> **Persona:** Abena Osei

## User Story

**As a** Abena Osei
**I want** Filing a child under a parent request updates the parent's spawned work cell in the same write
**So that** CR0683 is delivered by work that can be planned and checked

## Acceptance Criteria

### AC1: Filing a finding under a parent leaves no spawned-work drift

- **Given** a project whose RFC index carries a spawned-work column and an RFC with no children
- **When** a change request is filed with `file_finding.py file --parent <RFC>`
- **Then** the RFC's row in the index names the new child in its spawned-work cell in the same write, and `reconcile.py --dry-run` reports no spawned-column drift. Fails on: the cell left as it was until `reconcile apply` runs, so the next commit is refused on drift
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_file_finding.py::ParentSpawnedCellTests::test_filing_under_a_parent_writes_the_parents_spawned_work_cell

### AC2: Creating an artefact under a parent leaves no spawned-work drift

- **Given** the same project and an RFC that already has one child
- **When** a second child is created with `artifact.py new --parent <RFC>`
- **Then** the RFC's spawned-work cell names both children, the earlier one kept, and `reconcile.py --dry-run` reports no spawned-column drift. Fails on: the earlier child dropped from the cell, or the cell untouched
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_artifact.py::ParentSpawnedCellTests::test_new_under_a_parent_writes_the_parents_spawned_work_cell

### AC3: A parent whose index has no spawned-work column still takes a child

- **Given** a parent request whose index table has no spawned-work column
- **When** a child is filed under it with `file_finding.py file --parent <id>`
- **Then** the child is minted with both link directions wired as today, the index gains no column, and the command exits 0. Fails on: a crash or a refusal where there is no cell to write, or a column invented in the index
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_file_finding.py::ParentSpawnedCellTests::test_a_parent_index_with_no_spawned_column_still_takes_the_child

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-17 | sdlc-studio | Created via `new` (deterministic) |
