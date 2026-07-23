# EP0153: A reproducible seat brief

> **Status:** In Progress
> **Derived Point Total:** 9
> **Parent:** CR0409
> **Created:** 2026-07-23
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Size:** L

## Summary

Decomposed from CR0409. Delivers the work CR0409 requested.

## Story Breakdown

- [ ] [US0404: emit the seat brief derived from run state, worklist, planner output and lessons, naming the grooming state](../stories/US0404-emit-the-seat-brief-derived-from-run-state.md)
- [ ] [US0405: the brief is recorded with the verdicts so a thin brief is visible](../stories/US0405-the-brief-is-recorded-with-the-verdicts-so.md)
- [ ] [US0406: goal-review record accepts a --fields-file so no seat prose crosses a shell](../stories/US0406-goal-review-record-accepts-a-fields-file-so.md)

## Acceptance Criteria (Epic Level)

- [ ] A command emits the seat brief for the current batch and goal, derived from the run state, the worklist and the planner's own output, so the same batch briefs the same way every time.
- [ ] The brief names the batch's grooming state - placeholder acceptance criteria, shared-file clusters, the reachable end state - because those are what the first live review turned on.
- [ ] The brief that was given is recorded with the verdicts, so a thin review is visible as a thin brief rather than as a seat that found nothing.
- [ ] goal-review record accepts a --fields-file document, so no seat's prose crosses a shell. Fold this into CR0392 rather than building a second path.

> Carried from the request. Author each story's own ACs against its
> slice while grooming - these are the epic's completion bar, not any
> single story's.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-23 | sdlc-studio | Created via `new` (deterministic) |
