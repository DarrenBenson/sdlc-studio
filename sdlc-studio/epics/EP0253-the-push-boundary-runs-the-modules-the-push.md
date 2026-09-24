# EP0253: The push boundary runs the modules the push changed, and says which

> **Status:** Superseded
> **Closed with findings in:** D0265 backlog sweep 2026-09-24 (sdlc-studio/reviews/backlog-sweep-2026-09-24.md), SUPERSEDED
> **Derived Point Total:** 16
> **Parent:** CR0586
> **Created:** 2026-09-16
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Size:** L

## Summary

Decomposed from CR0586. Delivers the work CR0586 requested.

## Story Breakdown

- [x] [US0824: module-alone at the push boundary runs the changed modules and everything that imports them](../stories/US0824-module-alone-at-the-push-boundary-runs-the.md)
- [x] [US0825: the lane line names its selection and the rule that produced it, so a narrowed lane is never read as a full one](../stories/US0825-the-lane-line-names-its-selection-and-the.md)
- [x] [US0826: the full 133-module sweep runs on the schedule, and a week with no scheduled run is reported rather than silently skipped](../stories/US0826-the-full-133-module-sweep-runs-on-the.md)
- [x] [US0827: a module the selection omitted and the sweep later finds red is recorded as a miss, so the rule is judged on evidence](../stories/US0827-a-module-the-selection-omitted-and-the-sweep.md)
- [x] [US0843: module-alone prints the per-module wall clock it already computes, so a narrowing can be judged before it is built](../stories/US0843-module-alone-prints-the-per-module-wall-clock.md)

## Acceptance Criteria (Epic Level)

- [ ] The push boundary runs the changed modules and their importers, and the lane's line names the selection and the rule that produced it
- [ ] The full sweep still runs on the schedule, and a week with no scheduled run is reported rather than silently skipped
- [ ] A module that the selection omits and the full sweep later finds red is recorded as a miss, so the rule's cost is measurable rather than asserted
- [ ] The push gate's measured wall clock is recorded before and after, beside `gate_timing`'s estimate

> Carried from the request. Author each story's own ACs against its
> slice while grooming - these are the epic's completion bar, not any
> single story's.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-16 | sdlc-studio | Created via `new` (deterministic) |
| 2026-09-24 | Claude Opus 5.5 | Backlog sweep D0265 (sdlc-studio/reviews/backlog-sweep-2026-09-24.md): SUPERSEDED - module-alone narrowing at push: US0881 moved module-alone to the release boundary |
