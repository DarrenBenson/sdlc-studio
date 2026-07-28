# EP0179: The loop measures its own cost and carries its own learning forward

> **Status:** Draft
> **Parent:** CR0462
> **Derived Point Total:** 29
> **Parent:** CR0464
> **Created:** 2026-07-28
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Size:** XL

## Summary

Decomposed from CR0464. Delivers the work CR0464 requested.

## Story Breakdown

- [ ] [US0518: The retro curates a fixed-size set of carried lessons, and the content check requires it](../stories/US0518-the-retro-curates-a-fixed-size-set-of.md)
- [ ] [US0519: A lesson earns a place only by displacing one, and the displaced lesson is named with the reason](../stories/US0519-a-lesson-earns-a-place-only-by-displacing.md)
- [ ] [US0520: The sprint reads the carried lessons at plan and puts them in every delivery lane's brief and the reviewers'](../stories/US0520-the-sprint-reads-the-carried-lessons-at-plan.md)
- [ ] [US0521: A lesson violated again after being carried is reported at the close, naming the unit that repeated it](../stories/US0521-a-lesson-violated-again-after-being-carried-is.md)
- [ ] [US0522: A repeatedly violated lesson can propose a change request or bug for the operator to accept or decline](../stories/US0522-a-repeatedly-violated-lesson-can-propose-a-change.md)
- [ ] [US0523: The close reports delivery time against overhead time as a ratio, beside the points and token figures](../stories/US0523-the-close-reports-delivery-time-against-overhead-time.md)
- [ ] [US0524: An unmeasured component is reported as unmeasured rather than as zero, and the ratio is written to the velocity record](../stories/US0524-an-unmeasured-component-is-reported-as-unmeasured-rather.md)

## Acceptance Criteria (Epic Level)

- [ ] The carried set is FIXED SIZE and changes only by displacement: each retro asks of every lesson the batch produced whether it is more important than anything already carried, and a lesson that earns a place names the one it displaces and why. Adding without displacing is refused, because a set that can grow is a set nobody reads - which is the condition the 252-entry summary is already in.
- [ ] The retro produces a curated summary of the few lessons that matter most for the NEXT batch - a written judgement, not a ranking - and the retro's content check requires it.
- [ ] The sprint reads that summary at plan time and carries it into every delivery lane's brief, so it reaches the agent doing the work rather than only the operator watching.
- [ ] The reviewers receive it too, so the pass most likely to catch a repeat is told what has been repeating.
- [ ] A lesson violated again after being carried is reported at the close, naming the unit that repeated it - a repeat is evidence the lesson needs a guard, not a louder note.
- [ ] A lesson that has been repeatedly violated can propose a change request or bug for the operator to accept or decline, so the loop ends in work rather than in a longer list.
- [ ] The curated set is re-decided each retro rather than accumulating, so it stays small enough to be read and current enough to be worth reading.

### From CR0462

- [ ] The close reports delivery time against overhead time - gate, review, re-runs and repair cycles - as a ratio, alongside the points and token figures it already carries.
- [ ] The figures are derived from what the run recorded rather than estimated at close, and a component that was not measured is reported as unmeasured rather than as zero.
- [ ] The ratio is written to the velocity record so the trend across sprints is visible, since a single sprint's ratio says little and the direction says everything.

> Carried from the request. Author each story's own ACs against its
> slice while grooming - these are the epic's completion bar, not any
> single story's.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-28 | sdlc-studio | Created via `new` (deterministic) |
