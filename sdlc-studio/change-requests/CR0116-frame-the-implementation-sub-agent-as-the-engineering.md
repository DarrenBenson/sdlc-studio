# CR-0116: Frame the implementation sub-agent as the Engineering persona/seat, not a generic agent

> **Status:** Complete
> **Priority:** Medium
> **Type:** Improvement
> **Date:** 2026-06-25
> **Created-by:** sdlc-studio file

## Summary

The skill's persona/seat machinery is entirely review-side: RFC0016 seats (Product/Engineering/QA) are charters consulted to REVIEW artefacts (Spec Review, the independent critic). But when the sprint loop DELEGATES implementation - the agentic wave or a sub-agent build - reference-agent-prompt-template.md carries no persona framing, so the builder is a blank general-purpose agent. A field agent delivering EP0005 spawned a generic general-purpose sub-agent for the whole SPA build; the operator asked why not the Engineer persona. Frame the implementer with the Engineering seat charter (engineering discipline, the project's conventions + best-practices, the quality bar) so the builder works AS the engineer, not an identity-less agent. KEY constraint: the independent critic must remain a SEPARATE Engineering-seat instance - the building seat and the reviewing seat are different subagents, never self-review (preserve author/critic separation).

> **Depends on:** CR0117 (the mechanical author != reviewer gate - the prerequisite all three
> seats insisted on).

## Acceptance Criteria (revised by the RFC0020 consult)

- [x] the wave-delegation prompt **appends a thin Engineering stance preamble** (the non-negotiables + shadow: tests must be able to fail; red gate is a stop; never weaken an AC to go green; no `any`) **AFTER** the existing contract - it never rewrites or dilutes READ THESE FILES FIRST / Files to Create-Modify-DO NOT Modify / AC / quality gates (the Engineering seat: those concrete sections are 80% of build quality)
- [x] the stance is a render-mode of the existing review-seat charter, not a forked heavyweight charter; persona text sits after the contract, never woven through it
- [x] `--skip-personas` yields a **byte-equivalent contract** that still builds and passes the same gated executable ACs (prove with a fixture wave both ways); the independence floor is preserved by CR0117 regardless of persona presence
- [x] the independent critic stays a separate seat instance (enforced by CR0117, not prose); the build seat never reviews its own output
- [x] documented in reference-agent-prompt-template.md + reference-workflow-personas.md; CHANGELOG entry

## Relationship

The **Engineering-build slice** of **RFC0020 (Maximise persona use)** - the operator's
lifecycle-wide direction that Product authors stories, Engineering builds, QA tests, and the
review seats review, each as its persona. The QA-test and Product-author slices live in RFC0020;
this CR is the proven first slice. Implement under RFC0020 once accepted.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-06-25 | audit | Raised |
| 2026-06-25 | audit | Linked as the Engineering slice of RFC0020 (maximise persona use); QA-test + Product-author are sibling slices in the RFC |
