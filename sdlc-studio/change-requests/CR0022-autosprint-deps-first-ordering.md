# CR-0022: Dependency-first ordering in autosprint plan

> **Status:** Complete
> **Priority:** High
> **Type:** Feature
> **Requester:** Autosprint (determinism-sprint retro)
> **Date:** 2026-06-20
> **Affects:** scripts/autosprint.py, scripts/audit.py (dependency read), reference-autosprint.md
> **Depends on:** --
> **GitHub Issue:** --

## Summary

`autosprint plan` orders a batch by priority/severity only. The tranche audit
already reads each unit's `Depends on` graph for readiness, but the **ordering**
ignores it, so a unit can be scheduled before the unit it depends on. In the
determinism sprint, CR0021 depended on CR0003 and had to be sequenced **by hand**;
an unattended `--order priority` run would have attempted CR0021 first and stalled
on the unmet dependency mid-flow.

## Problem

`select_batch` sorts by `(priority_weight, id)`. There is no topological pass over
`Depends on`. The loop therefore relies on the operator to hand-order
inter-dependent units - exactly the manual step the autosprint exists to remove.

## Proposed Changes

### Item 1: Topological order, priority as the tiebreak

**Priority:** High **Effort:** Medium

Add a dependency-topological pass to `select_batch`/`build_plan`: read each unit's
`Depends on` (the same field `audit.py` already parses), build the in-batch
dependency graph, and emit a stable topological order with priority/severity as the
tiebreak among ready units. Dependencies on units **outside** the batch are
surfaced (they are the audit's `unmet-deps`), not silently reordered. A dependency
cycle aborts with the cycle named (mirrors `project implement`).

## Impact Assessment

| Module | Impact | Change Type |
| --- | --- | --- |
| scripts/autosprint.py | Topological ordering before the priority tiebreak | Modified |
| scripts/audit.py | Dependency read reused (or lifted to a shared helper) | Reused |
| reference-autosprint.md | Document deps-first ordering | Modified |

### Breaking Changes

None. `--order priority` keeps priority as the tiebreak; output is unchanged for a
batch with no in-batch dependencies.

## Acceptance Criteria

- [x] Given units B (High) depends-on A (Low), both in the batch, `plan` orders A before B despite priority.
- [x] Given a dependency cycle A->B->A, `plan` aborts non-zero naming the cycle.
- [x] Given a dependency on a unit outside the batch, ordering does not reorder for it; the audit reports it as `unmet-deps`.
- [x] Priority/severity remains the tiebreak among units with no ordering constraint. Unit-tested.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-06-20 | Autosprint (tooling-honesty-sprint) | Complete - US0018: _topo_order (Kahn, priority tiebreak, cycle aborts); critic-approved after fixing prose-id phantom edges |
| 2026-06-20 | Autosprint (determinism-sprint retro) | Raised - ordering ignores Depends on; CR0021 had to be hand-sequenced after CR0003 |
