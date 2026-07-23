# EP0151: A rung-aware forecast and retro

> **Status:** Done
> **Derived Point Total:** 5
> **Parent:** CR0407
> **Created:** 2026-07-23
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Size:** M

## Summary

Decomposed from CR0407. Delivers the work CR0407 requested.

## Story Breakdown

- [x] [US0400: the forecast names the rung it prices and reads UNMEASURED where that rung has no rate](../stories/US0400-the-forecast-names-the-rung-it-prices-and.md)
- [x] [US0401: a non-done close records tokens with the tokens-per-point blank, and reference-sprint.md notes the rungs differ](../stories/US0401-a-non-done-close-records-tokens-with-the.md)

## Acceptance Criteria (Epic Level)

- [ ] The forecast states which rung it prices. A `--goal design` or `--goal plan` run does not silently present the build forecast as its own.
- [ ] Where no rate has been measured for the rung, the forecast reads UNMEASURED for that rung rather than substituting the build rate - the same refusal the cross-model rate check already makes.
- [ ] A run that closes at a non-`done` rung records its token spend WITHOUT a tokens-per-point figure, so no partial-rung row can contaminate the velocity record the planner re-measures from.
- [ ] reference-sprint.md states that the rungs cost differently and that only the build rung has a measured rate.

> Carried from the request. Author each story's own ACs against its
> slice while grooming - these are the epic's completion bar, not any
> single story's.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-23 | sdlc-studio | Created via `new` (deterministic) |
