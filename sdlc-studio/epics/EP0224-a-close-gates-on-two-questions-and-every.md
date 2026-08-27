# EP0224: A close gates on two questions, and every other step becomes a report

> **Status:** Draft
> **Derived Point Total:** 19
> **Parent:** CR0507
> **Created:** 2026-08-27
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Size:** L

## Summary

Decomposed from CR0507. Delivers the work CR0507 requested.

## Story Breakdown

- [ ] [US0717: The close GATES on the goal verdict and the stop-ship ruling, and on nothing else](../stories/US0717-the-close-gates-on-the-goal-verdict-and.md)
- [ ] [US0718: The stop-ship question is answered per defect and the ruling records who made it](../stories/US0718-the-stop-ship-question-is-answered-per-defect.md)
- [ ] [US0719: A sprint closes WITH open defects as the normal case, needing no waiver](../stories/US0719-a-sprint-closes-with-open-defects-as-the.md)
- [ ] [US0720: A verdict is judged on the revision it was given for, so a repaired REJECT does not gate for ever](../stories/US0720-a-verdict-is-judged-on-the-revision-it.md)
- [ ] [US0721: The close's own cost is measured and reported beside the delivery's](../stories/US0721-the-close-s-own-cost-is-measured-and.md)

## Acceptance Criteria (Epic Level)

- [ ] The close GATES on two questions and no others: is the Sprint Goal met (achieved / partial / missed, with its rationale), and is any OPEN defect a stop-ship. Every other current step becomes a derived report printed beside the verdict - stated, never blocking. A step that cannot answer its question reports UNKNOWN rather than refusing, on the same principle the repo already applies to a dead-flag destination it cannot judge.
- [ ] The stop-ship question is answered per defect and the ruling is RECORDED with who made it, since it is a judgement rather than a measurement. `judge_defects_against_goal` already exists and already answers it; it is currently one input among many rather than one of the two gates.
- [ ] A sprint closes with open defects. That is the normal case, not an exception needing a waiver: a close records what is carried and what it was ruled, and only a stop-ship holds it. The waiver machinery currently absorbing this (D0074, D0077-D0087) exists because closing over known issues has no first-class representation, and a waiver misdescribes what happened - nothing was bypassed, a judgement was made.
- [ ] A review verdict is judged on the REVISION it was given for. A REJECT that has been repaired is retired by a recorded re-review, and a stale verdict does not gate a close forever - this is CR0506, and it is a precondition rather than a sibling: without it the first gate cannot be satisfied by the ordinary reject-fix-rereview loop every human team uses.
- [ ] The close's own cost is measured and reported against the delivery's, because the failure this CR names is invisible until those two numbers sit side by side. A close costing more than the sprint it certifies is reported as the defect it is.

> Carried from the request. Author each story's own ACs against its
> slice while grooming - these are the epic's completion bar, not any
> single story's.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-27 | sdlc-studio | Created via `new` (deterministic) |
