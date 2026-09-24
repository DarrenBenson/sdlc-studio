# EP0171: In-flight sprint controls and a close review derived from one recorded entry

> **Status:** Done
> **Closed with findings in:** D0265 backlog sweep 2026-09-24 (sdlc-studio/reviews/backlog-sweep-2026-09-24.md), DELIVERED
> **Parent:** CR0424
> **Derived Point Total:** 27
> **Parent:** CR0441
> **Created:** 2026-07-27
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Size:** L

## Summary

Decomposed from CR0441. Delivers the work CR0441 requested.

## Story Breakdown

- [x] [US0469: Every sprint batch change reports its capacity effect through the plan-time renderer: points and token forecast against capacity.tokens, unit count against the appetite](../stories/US0469-every-sprint-batch-change-reports-its-capacity-effect.md)
- [x] [US0470: sprint batch swap trades units in one recorded call, in the house id grammar, reporting whether the points balanced](../stories/US0470-sprint-batch-swap-trades-units-in-one-recorded.md)
- [x] [US0471: sprint batch add-epic adds an epic's stories at a named status as one set, priced through the shared renderer](../stories/US0471-sprint-batch-add-epic-adds-an-epic-s.md)
- [x] [US0472: The appetite can be resized on an open run with a recorded reason, and the standing capacity it is measured against survives the resize](../stories/US0472-the-appetite-can-be-resized-on-an-open.md)
- [x] [US0473: The in-flight sprint controls are documented as runnable invocations, with coverage derived from the parser and the reference section pinned structurally](../stories/US0473-the-in-flight-sprint-controls-are-documented-as.md)
- [x] [US0474: review_prep derives the RV record and stamps the covered units from one recorded sprint-review APPROVE, without touching operator prose](../stories/US0474-review-prep-derives-the-rv-record-and-stamps.md)
- [x] [US0475: The sprint close derives the review record ahead of the gate, and the review-current lane demonstrably clears on a git fixture](../stories/US0475-the-sprint-close-derives-the-review-record-ahead.md)

## Acceptance Criteria (Epic Level)

- [ ] batch add and drop report the capacity effect of the change - the unit's points, the batch total before and after, and the appetite it is now measured against - so a mutation is never silent about what it did to the plan.
- [ ] A swap is one operation: bringing a unit in while taking named units out is a single call that reports whether the point totals balanced, and warns when they did not, rather than requiring two calls that cannot see each other.
- [ ] An epic can be added in one move, adding its plannable stories as a set and reporting the combined points against the appetite rather than requiring one call per story.
- [ ] The appetite can be changed on an open run, recorded with a reason on the run state, so making a sprint bigger is a stated decision with a trail rather than a number silently exceeded.
- [ ] A batch change that takes the committed points past the appetite is reported plainly at the moment it happens; it is not refused, because an operator may knowingly overcommit, but it is never silent.

### From CR0424

- [ ] A recorded critic sprint-review APPROVE covering the batch can satisfy the close review-current lane directly, or the close derives the RV and anchor from it, so the review is entered once

> Carried from the request. Author each story's own ACs against its
> slice while grooming - these are the epic's completion bar, not any
> single story's.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-27 | sdlc-studio | Created via `new` (deterministic) |
| 2026-09-24 | Claude Opus 5.5 | Backlog sweep D0265 (sdlc-studio/reviews/backlog-sweep-2026-09-24.md): DELIVERED - its close derives Done: US0470 to US0473 were delivered, and the three open stories are superseded by US0870, US0875 and US0876; planning ruled it SUPERSEDED |
