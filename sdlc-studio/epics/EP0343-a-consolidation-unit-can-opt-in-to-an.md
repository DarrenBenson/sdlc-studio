# EP0343: A consolidation unit can opt in to an ownership line, kept only if a measured trial earns it

> **Status:** Draft
> **Derived Point Total:** 9
> **Parent:** CR0701
> **Created:** 2026-11-17
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Size:** L

## Summary

Decomposed from CR0701. Delivers the work CR0701 requested.

## Story Breakdown

- [ ] [US1247: A unit that opts in gets the ownership line naming its Affects in its lane brief, and nothing else carries it](../stories/US1247-a-unit-that-opts-in-gets-the-ownership.md)
- [ ] [US1248: The bench runs an ownership arm on the brownfield fixtures, reporting priced tokens, score and duplication](../stories/US1248-the-bench-runs-an-ownership-arm-on-the.md)
- [ ] [US1249: The sprint report sets each opted-in unit against comparable units, so the keep-or-drop rule can be judged](../stories/US1249-the-sprint-report-sets-each-opted-in-unit.md)

## Acceptance Criteria (Epic Level)

- [ ] A story or bug can declare that it opts in; its lane brief then carries the ownership line naming its Affects, and a unit that does not opt in carries no ownership line
- [ ] No reviewer brief from critic.py brief, no agent definition, and neither AGENTS.md nor the shipped agent-instructions template carries the ownership line, and a test pins that
- [ ] The line is first measured on the bench (tools/bench) as an ownership arm beside the pipeline arm on the brownfield fixtures, reporting priced tokens, the held-back suite score and duplicated lines before and after, counted by one stated tool
- [ ] The first three opted-in sprint units are reported against comparable units of the same size: priced tokens per point, review rounds, out-of-Affects blockers raised and duplicated lines removed
- [ ] The keep-or-drop rule is recorded as a decision before the trial starts (proposed: keep only if at least two of the three units remove the duplication their criteria name and priced tokens per point rises by no more than 25%), and the result is recorded against it

> Carried from the request. Author each story's own ACs against its
> slice while grooming - these are the epic's completion bar, not any
> single story's.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-17 | sdlc-studio | Created via `new` (deterministic) |
