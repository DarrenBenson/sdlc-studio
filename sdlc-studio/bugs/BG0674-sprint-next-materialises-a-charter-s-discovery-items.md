# BG0674: sprint next materialises a charter's discovery items (CRs) that sprint plan then refuses, so the charter at the head of the queue produces a batch nothing can plan

> **Status:** Open
> **Severity:** Medium
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py
> **Created:** 2026-09-15
> **Created-by:** sdlc-studio file
> **Raised-by:** backlog sweep 2026-09-15; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

`sprint.py next` resolves the head charter's scope query and materialises whatever it selects, including CRs, RFCs and Issues. `sprint plan` refuses those same units as 'DISCOVERY items, not deliverable work'. Reproduced in a throwaway clone at 51f264db: the queue head is SC0004 (query `--crs Proposed`); `next --dry-run` prints 'materialised 11 unit(s) ... CR0545, CR0523, CR0524, CR0543, CR0544, CR0557, CR0562, CR0563, CR0566, CR0567, CR0511', and `plan --crs Proposed` exits 2 'sprint plan REFUSED: 11 unit(s) are DISCOVERY items'. SC0004's query also no longer selects the CR its goal names (CR0497, now In Progress), and SC0001's has the same shape - both are separate content fixes. Found by the 2026-09-15 backlog sweep.

## Steps to Reproduce

1. In a throwaway clone, `python3 .claude/skills/sdlc-studio/scripts/sprint.py queue show` - SC0004 heads the queue with `--crs Proposed`.
2. `sprint.py next --dry-run` - it materialises 11 Proposed CRs.
3. `sprint.py plan --crs Proposed` - exit 2, the same 11 refused as discovery items.

## Proposed Fix

Apply plan's discovery refusal when `next` materialises, so a charter whose query selects discovery items is refused (or its discovery items named and excluded) at `next`, with the remedy - refine the request, or point the query at its decomposition - rather than at the plan that follows.

## Acceptance Criteria

- [ ] **AC1** `sprint next` on a charter whose query selects only discovery items refuses, naming them and the remedy, and materialises nothing
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::NextRefusesDiscoveryItemsTests::test_a_discovery_only_query_is_refused_at_next
- [ ] **AC2** `sprint next` on a charter whose query selects deliverable units materialises them as today - the paired control
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::NextRefusesDiscoveryItemsTests::test_a_deliverable_query_materialises
- [ ] **AC3** A query selecting both kinds names the discovery items it did not materialise
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::NextRefusesDiscoveryItemsTests::test_a_mixed_query_names_what_it_dropped

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-15 | backlog sweep 2026-09-15 | Filed |
