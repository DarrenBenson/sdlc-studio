# EP0191: A repair is held by a mutant it kills: mutation is mandatory on a fix, gated on survivors at the transition

> **Status:** Draft
> **Derived Point Total:** 15
> **Parent:** CR0501
> **Created:** 2026-07-29
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Size:** L

## Summary

Decomposed from CR0501. Delivers the work CR0501 requested.

## Story Breakdown

- [ ] [US0564: A unit typed as a repair requires mutation evidence over its own changed lines before it can reach a terminal status](../stories/US0564-a-unit-typed-as-a-repair-requires-mutation.md)
- [ ] [US0565: The gate is the SURVIVOR count over those lines, and a surviving mutant refuses the transition naming the mutant and its line](../stories/US0565-the-gate-is-the-survivor-count-over-those.md)
- [ ] [US0566: Feature work keeps the cheaper bar, and a repair with no mutatable surface RECORDS that rather than being silently exempt](../stories/US0566-feature-work-keeps-the-cheaper-bar-and-a.md)
- [ ] [US0567: The shipped doctrine states that a fix's author is not sufficient evidence for that fix, so a consuming project inherits the mechanism not only the lesson](../stories/US0567-the-shipped-doctrine-states-that-a-fix-s.md)

## Acceptance Criteria (Epic Level)

- [ ] A unit typed as a repair - a bug fix, a review-residue fix, a regression fix - requires mutation evidence over its own changed lines before it can reach a terminal status.
- [ ] The gate is the SURVIVOR count over those lines, not merely that a mutation run happened; a surviving mutant refuses the transition and names the mutant and its line.
- [ ] The demand is made at the transition, beside the existing verification-depth requirement, so the claim and its evidence are checked in one place.
- [ ] Feature work is not subjected to the same bar, so the requirement stays affordable and does not get switched off wholesale.
- [ ] A repair with no mutatable surface RECORDS that fact rather than being silently exempt.
- [ ] The shipped doctrine states the rule that a fix's author is not sufficient evidence for that fix, so a consuming project inherits the mechanism and not only the lesson.

> Carried from the request. Author each story's own ACs against its
> slice while grooming - these are the epic's completion bar, not any
> single story's.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-29 | sdlc-studio | Created via `new` (deterministic) |
