# EP0206: A sprint ends with nothing open: a non-stop-ship finding becomes a bug and its story closes pointing at it

> **Status:** Draft
> **Derived Point Total:** 27
> **Parent:** CR0526
> **Created:** 2026-08-02
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Size:** L

## Summary

Decomposed from CR0526. Delivers the work CR0526 requested.

## Story Breakdown

- [ ] [US0625: the doctrine states CR0526's rule, names the one store a stop-ship ruling lives in, and who rules it](../stories/US0625-the-doctrine-states-cr0526-s-rule-names-the.md)
- [ ] [US0626: an unfinished batch unit holds the close through its stop-ship step, naming where its findings went, while Review and rung-end units do not](../stories/US0626-an-unfinished-batch-unit-holds-the-close-through.md)
- [ ] [US0627: a story or bug reaching Done or Fixed over an unanswered REJECT is refused until its findings are filed or the REJECT is repaired](../stories/US0627-a-story-or-bug-reaching-done-or-fixed.md)
- [ ] [US0628: a unit closed over a REJECT names, in its own record, the artefact its findings were filed to](../stories/US0628-a-unit-closed-over-a-reject-names-in.md)
- [ ] [US0823: every other route that ends a run reads the same unanswered-unit predicate as the close, and stop --force records what it waived](../stories/US0823-every-other-route-that-ends-a-run-reads.md)

## Acceptance Criteria (Epic Level)

- [ ] The doctrine states the rule: a non-stop-ship finding is filed as its own artefact and the story closes pointing at it; a stop-ship finding holds the close
- [ ] An unfinished batch unit holds the close through its stop-ship step (D0193, answered states consolidated in D0196), and every route that ends a run names it, together with the artefact its findings moved to - units at Review, Fixed or their rung's end, parked on a pending decision (and their dependants), dropped with a reason, or ruled in the carried table are answered, EXCEPT any unit whose standing REJECT `critic.coverage_state` does not read as fully closed (D0196c), whatever its status
- [ ] A story or bug reaching a delivered terminal over a recorded REJECT requires the finding to have somewhere to live: a filed artefact id, or a complete repair; a stop-ship ruling holds the close instead of discharging the REJECT (D0194)
- [ ] The stop-ship judgement lives in one store - the retro's Known issues carried table, which the close reads - and the doctrine names it and who rules (D0194)
- [ ] A story or bug closed this way names the bug in its own record, so a reader of the story learns where the work went without consulting the retro

> Carried from the request. Author each story's own ACs against its
> slice while grooming - these are the epic's completion bar, not any
> single story's.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-02 | sdlc-studio | Created via `new` (deterministic) |
| 2026-09-15 | sprint planning 2026-09-15 | Epic-level criteria amended to D0193, D0194 and D0195 at the sprint goal review: the close hold rides the stop-ship step with named answered states, a stop-ship ruling holds rather than discharges, one stop-ship store, and bugs as well as stories. |
| 2026-09-15 | sprint planning 2026-09-15 | Goal review round 4 notes (all three seats YES): epic criterion 2 carries D0196: dependants of a parked unit are answered, and any unit whose standing REJECT critic.coverage_state does not read as fully closed is not. |
