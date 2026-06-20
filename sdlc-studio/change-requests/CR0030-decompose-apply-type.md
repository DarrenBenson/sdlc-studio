# CR-0030: decompose apply_type (refactor-first on RFC0009's own signal)

> **Status:** Complete
> **Priority:** Medium
> **Type:** Improvement
> **Requester:** Darren Benson
> **Date:** 2026-06-20
> **Affects:** scripts/reconcile.py
> **Depends on:** CR0028 (the complexity signal that flagged it), CR0026 (apply_type + its corruption-guard tests)
> **GitHub Issue:** --

## Summary

Closing the refactor-first loop: `complexity.py` (RFC0009 WS1) flagged
`reconcile.apply_type` as the repo's top hotspot at **cognitive 56**. Decompose it
into small, single-purpose helpers, reducing it to **7**, with behaviour held
identical by the CR0026 corruption-guard suite (idempotency, escaped-pipe, summary
anchoring) as the safety net.

## Problem

`apply_type` carried the whole status-fix + summary-recompute + line-rewrite logic
inline (cognitive 56) - exactly the shape RFC0009 says costs more tokens, iterations
and error rate to change, and the kind of function its refactor-first recommendation
exists to catch.

## Proposed Changes

Extract `_plan_status_fixes`, `_row_id`, `_summary_cell_rewrite`, `_data_row_rewrite`,
`_header_kind` and `_rewrite_index_lines`; leave `apply_type` a thin orchestrator. No
behaviour change. Add a regression guard so it cannot silently regrow.

## Impact Assessment

| Module | Impact | Change Type |
| --- | --- | --- |
| scripts/reconcile.py | apply_type decomposed (56 -> 7); 6 helpers extracted | Refactor |

### Breaking Changes

None. Pure refactor; the public `apply_type` signature and behaviour are unchanged.

## Acceptance Criteria

- [x] Behaviour identical: the full reconcile suite (incl. CR0026 corruption-guards) passes; an independent critic confirmed equivalence via a differential probe.
- [x] `apply_type` cognitive complexity is reduced below 15 (was 56), guarded by a regression test.
- [x] Extracted helpers are each low-complexity and single-purpose.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-06-20 | Autosprint (CR0030) | Complete - US0028: apply_type 56 -> 7; 6 helpers; regression guard; critic APPROVE (behaviourally identical) |
| 2026-06-20 | Darren Benson | Raised - act on RFC0009's own refactor-first recommendation for the top hotspot |
