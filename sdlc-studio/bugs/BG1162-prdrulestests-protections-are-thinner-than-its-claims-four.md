# BG1162: PrdRulesTests' protections are thinner than its claims: four PRD facts can drift past it

> **Status:** Open
> **Severity:** Low
> **Points:** 2
> **Affects:** tools/tests/test_lean_prd_refresh.py, sdlc-studio/prd.md, changelog.d/US1104.md
> **Evidence:** sdlc-studio/reviews/critic-verdicts.md, US1104 APPROVE by qa-seat-US1104-r1 (brief d21783422d23).
> **Created:** 2026-11-01
> **Created-by:** sdlc-studio file
> **Raised-by:** claude; human; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-01T07:17:05Z

## Summary

qa-seat-US1104-r1's APPROVE of US1104 (2026-11-01) found four low gaps in tools/tests/`test_lean_prd_refresh.py`, each a claim the PRD gets right today. (1) The Security NFR's network scan (:619-623) recognises only a `["gh"` list, a `"fetch", "origin"` pair and stdlib HTTP clients, so a new `git ls-remote`, `git pull` or `("gh", ...)` caller goes unlisted. Three such mutants survived. (2) The breakdown business rule in prd.md §4 and changelog.d/US1104.md:6-8 apply the split ceiling only to a story or bug, but sprint.py:2159 refuses any pointed unit above it, a CR included. (3) `cost_problems` (:873) checks only that `estimate.tokens_per_point` is named, not that the override wins over the measured rate (sprint.py:194-215). (4) `tick_problems` (:952-955) accepts any open bug as the holder of a criterion, so reassigning Verify AC's criterion from BG1023 to BG0959 survived.

## Steps to Reproduce

1. In a throwaway worktree, add a `git ls-remote` call to readiness.py and run PrdRulesTests: green.
2. `sprint.py breakdown` on a fixture with a 13-point CR: refused, though the PRD rule names stories and bugs only.
3. Reverse the override-versus-rate order in the PRD: green.
4. Reassign the Verify AC criterion's holder to BG0959: green.

## Proposed Fix

Widen the network scan to any subprocess call whose argv names gh or a network git verb. Say 'any pointed unit' in the rule and the fragment. Assert that the override precedes the measured rate. Match each held criterion to the bug its text names.

## Acceptance Criteria

- [ ] **AC1** A script given a git ls-remote or a gh tuple call fails the Security NFR check until the PRD lists it.
  - **Verify:** pytest tools/tests/test_lean_prd_refresh.py
- [ ] **AC2** The PRD's breakdown rule and US1104's fragment name the split ceiling for any pointed unit.
  - **Verify:** pytest tools/tests/test_lean_prd_refresh.py
- [ ] **AC3** Reversing the override-versus-rate order, or reassigning a held criterion to another open bug, fails PrdRulesTests.
  - **Verify:** pytest tools/tests/test_lean_prd_refresh.py

## Impact

Four PRD facts could become false with the suite green.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-01 | claude | Filed |
