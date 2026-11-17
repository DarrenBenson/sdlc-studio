# EP0360: The sprint plan and report state the machinery share by theme and by path

> **Status:** Draft
> **Derived Point Total:** 10
> **Parent:** CR0722
> **Created:** 2026-11-17
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Size:** L

## Summary

Decomposed from CR0722. Delivers the work CR0722 requested.

## Story Breakdown

- [ ] [US1280: Sprint plan prints points by area from the tags and from a path map, naming any unit whose tag disagrees](../stories/US1280-sprint-plan-prints-points-by-area-from-the.md)
- [ ] [US1281: Sprint plan reports a missing maintenance declaration over one third machinery and still exits 0](../stories/US1281-sprint-plan-reports-a-missing-maintenance-declaration-over.md)
- [ ] [US1282: The sprint report carries the same two machinery shares as the plan printed](../stories/US1282-the-sprint-report-carries-the-same-two-machinery.md)

## Acceptance Criteria (Epic Level)

- [ ] Given a batch whose units carry an area tag and an Affects list, when sprint plan runs, then it prints the batch's points by area twice, once from the tags and once from a path map over each unit's Affects, and names any unit whose tag disagrees with the files it touches
- [ ] Given a plan whose machinery share is over one third by either reading and no maintenance declaration is recorded, when sprint plan runs, then it reports the missing declaration by name and still exits 0, as D0440 rules that nothing refuses the plan
- [ ] Given a closed run, when the sprint report is drawn, then it carries the same two shares as the plan printed
- [ ] RFC0063's Decomposed-into line and its WS7 row name this change request

> Carried from the request. Author each story's own ACs against its
> slice while grooming - these are the epic's completion bar, not any
> single story's.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-17 | sdlc-studio | Created via `new` (deterministic) |
