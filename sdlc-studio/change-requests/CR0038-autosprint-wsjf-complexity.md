# CR-0038: autosprint --order wsjf + complexity-weighted budget (RFC0009 WS3)

> **Status:** Complete
> **Priority:** Medium
> **Type:** Feature
> **Requester:** Autosprint (RFC0009)
> **RFC:** RFC-0009
> **Date:** 2026-06-20
> **Affects:** scripts/autosprint.py
> **Depends on:** CR0028 (complexity.py), RFC0001 (the loop)
> **GitHub Issue:** --

## Summary

Spawned from RFC0009 WS3, unblocked once both the autosprint loop (RFC0001) and the
complexity signal (CR0028) shipped. Replaces the `--order wsjf` stub (it fell back to
priority) with a real ordering: priority stays the dominant axis and the cognitive
complexity of a unit's `Affects` files (scored by complexity.py) breaks ties within a
priority, so the smaller blast-radius job goes first. The plan also carries a
complexity-weighted per-unit `token_budget`.

## Proposed Changes

- `autosprint.py`: `_affects_files` / `_resolve` / `_complexity_size`; `select_batch`
  attaches `complexity` + `token_budget` per unit under `--order wsjf`; `_topo_order`
  rank becomes (priority, complexity, id). Degrades to plain priority when no
  complexity is known; complexity never overrides priority; dependencies still win.

## Impact Assessment

| Module | Impact | Change Type |
| --- | --- | --- |
| scripts/autosprint.py | real WSJF ordering + token budget | Modified |

### Breaking Changes

None. `--order wsjf` previously aliased priority; it now refines within-priority by
complexity. With no `Affects` (the common case) the order is identical to priority.

## Acceptance Criteria

- [x] Within equal priority, a smaller-blast-radius unit is ordered before a larger one; the plan carries `complexity` + a complexity-scaled `token_budget`.
- [x] Priority dominates: an assessed higher-priority unit always precedes a degraded lower-priority one (size 0 never inflates above priority).
- [x] Dependencies still force order over the complexity tiebreak; the order degrades to priority when complexity is absent, unresolvable, or `complexity.assess` raises (no planning crash).
- [x] Unit-tested (priority-dominates, deps-vs-tiebreak, exception-degradation, Affects parsing); independent critic APPROVE after fixing the size-0 inflation + the backtick/paren parse.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-06-20 | Autosprint (RFC0009) | Complete - real --order wsjf; critic REJECT (size-0 inflation, parse order) -> fixed to priority-primary + 4 tests |
