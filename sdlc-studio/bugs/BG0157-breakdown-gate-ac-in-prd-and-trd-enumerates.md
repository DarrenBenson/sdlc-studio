# BG0157: Breakdown-gate AC in PRD and TRD enumerates size vocabularies the gate does not accept (Effort S/M/L, review-seat score)

> **Status:** Open
> **Severity:** Medium
> **Points:** 1
> **Affects:** sdlc-studio/prd.md, sdlc-studio/trd.md
> **Created:** 2026-07-16
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Fable 5 adversarial audit; agent; wf_9903a6e6-53a

## Summary

prd.md:284 and trd.md:878 (verbatim copies) say a unit is groomed by 'Effort: S/M/L, a story's Points:, or a review-seat score'. The implemented gate (sprint.py:1148-1157) accepts only Points for a story/bug and a T-shirt Size for a CR/RFC; Effort is retired (CR0265, never consulted) and a review-seat score is an ignorable WSJF input (--skip-personas), never a grooming size. An operator following the spec's enumerated acceptance signal (adding Effort: M) is still refused by the gate - the spec's oracle diverges from the implementation, and two artefacts agree on a meaning the code does not share (LL0016), while the enumeration silently blesses inputs the gate rejects (LL0013). Verified 3x; CR0265 shipped the vocabulary change without updating either spec.

## Steps to Reproduce

Add `Effort: M` (no Points) to an unsized story per prd.md:284's AC; run sprint plan - the breakdown gate still refuses the story as ungroomed.

## Proposed Fix

Correct the AC line in both prd.md:284 and trd.md:878: a story/bug is sized by Points, a CR/RFC/epic by a T-shirt Size; remove Effort and the review-seat score from the enumeration.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-16 | Claude Fable 5 adversarial audit | Filed |
