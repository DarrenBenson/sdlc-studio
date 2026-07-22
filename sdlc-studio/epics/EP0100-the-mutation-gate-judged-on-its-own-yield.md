# EP0100: The mutation gate judged on its own yield

> **Status:** Done
> **Derived Point Total:** 5
> **Parent:** CR0379
> **Created:** 2026-07-22
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Size:** M

## Summary

Decomposed from CR0379. Delivers the work CR0379 requested.

## Story Breakdown

- [x] [US0301: Each mutation run appends applied, killed, survived, unchecked and wall-clock to a series](../stories/US0301-each-mutation-run-appends-applied-killed-survived-unchecked.md)
- [x] [US0302: Artefacts filed from survivors link back, so yield is attributable to a run](../stories/US0302-artefacts-filed-from-survivors-link-back-so-yield.md)

## Acceptance Criteria (Epic Level)

- [ ] each mutation run records applied, killed, survived, un-checked-beyond-ceiling and wall-clock to a series file, not only to stdout
- [ ] a survivor that is later filed as an artefact links back to the run that found it, so yield is counted in artefacts rather than in survivor counts
- [ ] an equivalent mutant recorded as such is excluded from yield, since counting it would overstate the gate value
- [ ] the sprint report renders cost against yield for the run and the trailing history, so the trade is visible at the close where the decision is actually taken
- [ ] a run killed or timed out records that it produced no evidence, and is never readable as a clean run

> Carried from the request. Author each story's own ACs against its
> slice while grooming - these are the epic's completion bar, not any
> single story's.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-22 | sdlc-studio | Created via `new` (deterministic) |
