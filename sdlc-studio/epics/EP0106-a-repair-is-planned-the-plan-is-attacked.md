# EP0106: A repair is planned, the plan is attacked, and only then is it executed

> **Status:** Draft
> **Derived Point Total:** 15
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

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-22 | sdlc-studio | Created via `new` (deterministic) |
