# EP0281: A unit's criteria are shown by the tool to fail without its change before it closes

> **Status:** Draft
> **Parent:** CR0616
> **Derived Point Total:** 16
> **Parent:** CR0624
> **Created:** 2026-10-09
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Size:** L

## Summary

Decomposed from CR0624. Delivers the work CR0624 requested.

## Story Breakdown

- [ ] [US1017: transition set refuses a unit at Done or Fixed when none of its criteria fail with its change reverted](../stories/US1017-transition-set-refuses-a-unit-at-done-or.md)
- [ ] [US1018: The close and the sign judge each unit once, a preview never reverts, and the sign prints what the transition reported](../stories/US1018-the-close-and-the-sign-judge-each-unit.md)
- [ ] [US1019: A lane's return runs the revert check, so the builder learns its tests cannot fail before a reviewer does](../stories/US1019-a-lane-s-return-runs-the-revert-check.md)
- [ ] [US1020: The terminal transition names each criterion that passes without the change, even when the unit goes through](../stories/US1020-the-terminal-transition-names-each-criterion-that-passes.md)

## Acceptance Criteria (Epic Level)

- [ ] `transition -> Done` (story) and `-> Fixed` (bug) run revert-check over the unit's declared Affects and refuse a unit whose criteria stay green with the production change reverted, naming each criterion, unless `Revert-check-exempt` names it with a reason
- [ ] A unit whose production change cannot be isolated from its tests (no production path in Affects) is reported as not judged, never passed

> Carried from the request. Author each story's own ACs against its
> slice while grooming - these are the epic's completion bar, not any
> single story's.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-09 | sdlc-studio | Created via `new` (deterministic) |
