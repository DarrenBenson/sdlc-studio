# CR-0116: Frame the implementation sub-agent as the Engineering persona/seat, not a generic agent

> **Status:** Proposed
> **Priority:** Medium
> **Type:** Improvement
> **Date:** 2026-06-25
> **Created-by:** sdlc-studio file

## Summary

The skill's persona/seat machinery is entirely review-side: RFC0016 seats (Product/Engineering/QA) are charters consulted to REVIEW artefacts (Spec Review, the independent critic). But when the sprint loop DELEGATES implementation - the agentic wave or a sub-agent build - reference-agent-prompt-template.md carries no persona framing, so the builder is a blank general-purpose agent. A field agent delivering EP0005 spawned a generic general-purpose sub-agent for the whole SPA build; the operator asked why not the Engineer persona. Frame the implementer with the Engineering seat charter (engineering discipline, the project's conventions + best-practices, the quality bar) so the builder works AS the engineer, not an identity-less agent. KEY constraint: the independent critic must remain a SEPARATE Engineering-seat instance - the building seat and the reviewing seat are different subagents, never self-review (preserve author/critic separation).

## Acceptance Criteria

- [ ] the wave-delegation prompt template frames the implementer with the Engineering seat charter (discipline, project conventions/best-practices, quality bar) - the builder acts as the engineer
- [ ] the independent critic stays a separate Engineering-seat instance; the build seat never reviews its own output (author/critic separation preserved)
- [ ] the Engineering charter is referenced from a single source (review-seat-charter or a build variant); degrades gracefully when no personas exist (--skip-personas)
- [ ] documented in reference-agent-prompt-template.md + reference-workflow-personas.md; CHANGELOG entry

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-06-25 | audit | Raised |
