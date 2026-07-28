# EP0187: A sprint carries its goal in its name

> **Status:** Draft
> **Derived Point Total:** 8
> **Parent:** CR0471
> **Created:** 2026-07-28
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Size:** M

## Summary

Decomposed from CR0471. Delivers the work CR0471 requested.

## Story Breakdown

- [ ] [US0548: A sprint that surfaces as a file is named sprint-<run id>-<goal slug>, slugged by the shared helper](../stories/US0548-a-sprint-that-surfaces-as-a-file-is.md)
- [ ] [US0549: The bare run id stays canonical and resolves the sprint whatever the slug says, so rewording a goal orphans nothing](../stories/US0549-the-bare-run-id-stays-canonical-and-resolves.md)
- [ ] [US0550: A run with no goal recorded falls back to the id alone rather than inventing a slug](../stories/US0550-a-run-with-no-goal-recorded-falls-back.md)

## Acceptance Criteria (Epic Level)

- [ ] A sprint that surfaces as a file is named sprint-<run id>-<goal slug>, slugged from the Sprint Goal by the shared slug helper, proven by a test written red before the fix
- [ ] The bare run id remains the canonical identifier and resolves the sprint regardless of the slug, so rewording a goal does not orphan references, proven by a test that resolves a sprint whose recorded goal no longer matches its filename
- [ ] A run with no goal recorded falls back to the id alone rather than inventing a slug, proven by a test written red before the fix

> Carried from the request. Author each story's own ACs against its
> slice while grooming - these are the epic's completion bar, not any
> single story's.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-28 | sdlc-studio | Created via `new` (deterministic) |
