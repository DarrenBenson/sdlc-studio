# BG1154: Trevor's card says a sign-off on each unit is declined, though sprint.py sign writes a per-unit sign-off row under the one signature

> **Status:** Won't Fix
> **Severity:** Low
> **Points:** 1
> **Affects:** sdlc-studio/personas/trevor-hale-enterprise-pm.md, tools/tests/test_persona_coherence.py
> **Evidence:** US1081 APPROVE by qa-seat-US1081-r1 (brief 388418ce299a).
> **Created:** 2026-11-01
> **Created-by:** sdlc-studio file
> **Raised-by:** claude; human; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-01T04:52:48Z

## Summary

qa-seat-US1081-r1's APPROVE of US1081 (2026-11-01) found the sentence 'A sign-off on each unit, a second signature, or an approver on every ruling is his want, and is declined' (sdlc-studio/personas/trevor-hale-enterprise-pm.md:45). `sprint.py sign` writes a per-unit sign-off row for every unit under its one signature (D0213 ruling 3, and reference-sprint.md:139), so a reader can take the sentence to mean such rows do not exist. The card means a separate human sign-off act on each unit.

## Steps to Reproduce

1. Read trevor-hale-enterprise-pm.md:45.
2. Read D0213 ruling 3 and reference-sprint.md:139: per-unit sign-off rows are written at sign.

## Proposed Fix

Say 'a separate sign-off act on each unit', so the sentence is about the human act and not the rows sign writes.

## Acceptance Criteria

- [ ] **AC1** Trevor's card names the declined want as a separate sign-off act per unit, and states that the one signature writes each unit's sign-off row.
  - **Verify:** pytest tools/tests/test_persona_coherence.py

## Impact

A persona card, which reviewers and seats read as fact, contradicts the shipped sign step on one reading.

## Resolution

Won't Fix under D0564: the operator approved the product seat's proposal (D0562) because it is a wording preference, not a false statement. Trevor's card means a separate sign-off act; a wording preference in a persona card that no installed skill behaviour depends on. The qa re-check at 81e02369 found the defect still present (D0563), so this closes it as not worth its cost, not as fixed.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-01 | claude | Filed |
| 2026-11-21 | Claude Opus 5.5 (product seat, delegate under D0545) | Won't Fix under D0564: the operator approved the product seat's list (D0562); reason in Resolution |
