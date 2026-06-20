# US0018: Dependency-first batch ordering

> **Status:** Done
> **Epic:** [EP0007: Agentic Orchestration](../epics/EP0007-orchestration.md)
> **Owner:** Autosprint (CR0022, tooling-honesty-sprint)
> **Reviewer:** --
> **Created:** 2026-06-20
> **GitHub Issue:** --

## User Story

**As an** autosprint loop
**I want** the batch ordered deps-first, not by priority alone
**So that** an autonomous run never attempts a unit before the unit it depends on
(I had to hand-sequence CR0003 before CR0021 last sprint) (CR0022).

## Context

Implements CR0022. `autosprint.select_batch` now topologically orders the batch by
each unit's `Depends on` (the same field `audit.py` reads), with priority/severity
as the tiebreak among ready units. A dependency outside the batch is ignored (the
tranche audit reports it as unmet-deps); a cycle raises, and the CLI exits non-zero
naming it.

## Acceptance Criteria

### AC1: Deps come before dependents, overriding priority

- **Given** A (Low) and B (High) where B depends on A, both in the batch
- **When** `select_batch` orders them
- **Then** A precedes B despite B's higher priority
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_autosprint.py::DepsOrderTests::test_deps_first_overrides_priority
- **Verified:** yes (2026-06-20)

### AC2: A dependency cycle aborts, named

- **Given** A depends on B and B depends on A
- **When** ordering runs
- **Then** it raises `ValueError` naming the cycle (CLI exits non-zero)
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_autosprint.py::DepsOrderTests::test_cycle_raises
- **Verified:** yes (2026-06-20)

### AC3: Out-of-batch dependency ignored

- **Given** a unit depending on an id not in the batch
- **When** ordering runs
- **Then** it orders by priority with no error (the audit flags the unmet dep)
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_autosprint.py::DepsOrderTests::test_out_of_batch_dep_ignored
- **Verified:** yes (2026-06-20)

## Implementation

`scripts/autosprint.py`: `_topo_order(items, deps)` (Kahn, priority tiebreak, cycle
raises) wired into `select_batch`; `cmd_plan` returns non-zero on a cycle.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-06-20 | Autosprint (CR0022) | Decomposed from CR0022 (tooling-honesty sprint) |
