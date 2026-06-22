# CR-0065: Product Owner owns PRD and Product Manager owns PVD as review seats with requirements-met sign-off

> **Status:** Complete
> **Created:** 2026-06-22
> **Created-by:** sdlc-studio new
> **Priority:** Medium
> **Type:** Feature

## Summary

Formalise document ownership in the review-seat model and the review process: the **Product Owner**
seat is accountable for the **PRD**, the **Product Manager** seat for the **PVD**. Reviews must
verify the PRD (and PVD) requirements are actually met, recorded as an owned "requirements satisfied"
sign-off. Fixes the existing `workflow-personas.md` conflation (the product/PRD seat was mislabelled
"PM") and aligns with `reference-pvd.md` (PM owns PVD, PO owns PRD).

**Conditional scope:** the PVD is not needed in every project (single-repo products have none). When
there is no `sdlc-studio/product/pvd.md`, the **Product Manager seat and the PVD review leg do not
apply** - only the Product Owner + the PRD requirements-met sign-off run.

## Acceptance Criteria

- [ ] `reference-workflow-personas.md` defines two document-owner seats: **Product Owner** (owns the
  PRD) and **Product Manager** (owns the PVD); the old "PM" labels on PRD/requirements work are
  corrected to **Product Owner**.
- [ ] `reference-review.md`: the PRD leg records a Product-Owner **"PRD requirements satisfied"**
  sign-off; a new **PVD review leg** (with a Product-Manager "PVD requirements satisfied" sign-off and
  a PVD→PRD coverage check) runs **only when `sdlc-studio/product/pvd.md` exists**.
- [ ] The Product Manager seat + PVD leg are explicitly conditional - absent a PVD, neither applies.
- [ ] `reference-prd.md` / `reference-pvd.md` cross-reference the owning seat and its review sign-off;
  the agent-instructions starter notes the PVD leg is conditional.
- [ ] Lint + gate green; CHANGELOG entry; forward-ported.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-06-22 | sdlc | Created via `new` (deterministic) |
