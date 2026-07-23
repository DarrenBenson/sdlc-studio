# EP0114: The forecast prices the sprint, not just the build

> **Status:** Done
> **Derived Point Total:** 11
> **Parent:** CR0391
> **Created:** 2026-07-22
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Size:** L

## Summary

Decomposed from CR0391. Delivers the work CR0391 requested.

## Story Breakdown

- [x] [US0336: The forecast carries an explicit fixed per-sprint term alongside the per-point term, and the plan shows both rather than a single product](../stories/US0336-the-forecast-carries-an-explicit-fixed-per-sprint.md)
- [x] [US0337: The fixed term is MEASURED from the project's own velocity record, and reads UNMEASURED rather than a default where fewer than two sprints carry a whole-sprint actual](../stories/US0337-the-fixed-term-is-measured-from-the-project.md)
- [x] [US0338: A fit is never applied automatically: the plan states how many sprints it rests on and refuses to publish a fitted fixed term below a stated minimum](../stories/US0338-a-fit-is-never-applied-automatically-the-plan.md)
- [x] [US0339: The shipped seed's basis text states the condition under which a base term did worse, instead of claiming it flatly](../stories/US0339-the-shipped-seed-s-basis-text-states-the.md)

## Acceptance Criteria (Epic Level)

- [ ] The forecast carries an explicit fixed per-sprint term alongside the per-point term, and the plan shows both rather than a single product.
- [ ] The fixed term is MEASURED from the project's own velocity record where two or more sprints carry a whole-sprint actual, and reads UNMEASURED rather than a default where they do not.
- [ ] The shipped seed's basis text stops claiming a base term does worse, or states the condition under which that was true (runner-era per-unit data with no ceremony).
- [ ] A two-point fit is never applied automatically: the plan states how many sprints the fit rests on, and refuses to publish a fitted fixed term below a stated minimum.

> Carried from the request. Author each story's own ACs against its
> slice while grooming - these are the epic's completion bar, not any
> single story's.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-22 | sdlc-studio | Created via `new` (deterministic) |
