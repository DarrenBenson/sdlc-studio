# EP0106: A repair is planned, the plan is attacked, and only then is it executed

> **Status:** Draft
> **Parent:** CR0410
> **Derived Point Total:** 20
> **Parent:** RFC0053
> **Created:** 2026-07-22
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Size:** L

## Summary

Decomposed from RFC0053. Delivers the work RFC0053 requested.

## Story Breakdown

- [ ] [US0311: A REJECT verdict produces a written repair plan, one entry per finding, naming the change, the approach and what it might break](../stories/US0311-a-reject-verdict-produces-a-written-repair-plan.md)
- [ ] [US0312: The repair plan is attacked by an independent pass before any code is written, briefed with the four questions this loop keeps failing](../stories/US0312-the-repair-plan-is-attacked-by-an-independent.md)
- [ ] [US0313: A repair-plan verdict is PINNED to the findings it answers, so a later finding invalidates it](../stories/US0313-a-repair-plan-verdict-is-pinned-to-the.md)
- [ ] [US0314: A repair commit records which plan it executed, so a planned repair is distinguishable from an unplanned one](../stories/US0314-a-repair-commit-records-which-plan-it-executed.md)
- [ ] [US0315: The repair-plan gate is opt-in per project and OFF by default](../stories/US0315-the-repair-plan-gate-is-opt-in-per.md)
- [ ] [US0343: A repair answering a finding in the same class as a previous round must state whether the design is retained or changed, and a plan describing only a better instance is refused past the threshold](../stories/US0343-a-repair-answering-a-finding-in-the-same.md)
- [ ] [US0344: The reviewer brief asks whether the approach itself is the defect, and a recorded decision to RETAIN the design is a first-class outcome](../stories/US0344-the-reviewer-brief-asks-whether-the-approach-itself.md)

## Acceptance Criteria (Epic Level)

- [ ] When a repair answers a finding in the same class as a previous round's, the plan is required to state whether the DESIGN is being retained or changed, and why - a plan that only describes a better instance is refused once the threshold is reached.
- [ ] The threshold is configurable and its default is stated with the evidence it rests on, rather than being asserted as a round count somebody chose.
- [ ] The reviewer's brief carries the question explicitly: not only 'is this fix correct' but 'has this approach failed often enough that the approach is the defect'.
- [ ] A recorded decision to RETAIN the design is a first-class outcome, not a failure to change it - the point is that the question was asked and answered on the record.

> Carried from the request. Author each story's own ACs against its
> slice while grooming - these are the epic's completion bar, not any
> single story's.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-22 | sdlc-studio | Created via `new` (deterministic) |
