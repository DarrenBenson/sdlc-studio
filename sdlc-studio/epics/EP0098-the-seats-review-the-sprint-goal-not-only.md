# EP0098: The seats review the Sprint Goal, not only the ordering

> **Status:** Done
> **Derived Point Total:** 8
> **Parent:** CR0354
> **Created:** 2026-07-22
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Size:** M

## Summary

Decomposed from CR0354. Delivers the work CR0354 requested.

## Story Breakdown

- [x] [US0297: The plan puts the Sprint Goal to the resolved seats and records achievability and definition of done](../stories/US0297-the-plan-puts-the-sprint-goal-to-the.md)
- [x] [US0298: A goal unreachable by construction is detected and named at plan time](../stories/US0298-a-goal-unreachable-by-construction-is-detected-and.md)

## Acceptance Criteria (Epic Level)

- [ ] sprint plan consults the review seats on the Sprint Goal and batch coherence, not only for WSJF scores: is the goal achievable by this batch, what does done mean for it, and does the batch hang together as one increment
- [ ] the seat verdict is recorded on the run state at plan time, so the close judges the goal against what the seats said THEN rather than a later reconstruction
- [ ] the consult is BLOCKING at --goal plan - a plan whose goal no seat has reviewed is not written. Recommended over advisory: this run is a clean example of what advisory bought, and the check is cheap. If the operator prefers advisory, only this criterion changes
- [ ] a goal that no seat can judge achievable is reported with the reason, and the plan names the reachable end state instead of writing the aspirational one
- [ ] --skip-personas remains the recorded escape and says on the plan that the goal went unreviewed, so the close can see it

> Carried from the request. Author each story's own ACs against its
> slice while grooming - these are the epic's completion bar, not any
> single story's.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-22 | sdlc-studio | Created via `new` (deterministic) |
