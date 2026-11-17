# EP0323: A planned unit's Affects or criterion is amended in flight by a command that records why

> **Status:** Draft
> **Derived Point Total:** 8
> **Parent:** CR0656
> **Created:** 2026-11-17
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Size:** M

## Summary

Decomposed from CR0656. Delivers the work CR0656 requested.

## Story Breakdown

- [ ] [US1185: sprint batch amend widens a batch unit's Affects with a reason, writes its revision row and records it on the run](../stories/US1185-sprint-batch-amend-widens-a-batch-unit-s.md)
- [ ] [US1186: sprint batch amend rewords a batch unit's criterion with a reason, and refuses a unit already reviewed in the run](../stories/US1186-sprint-batch-amend-rewords-a-batch-unit-s.md)
- [ ] [US1187: The sprint report of a closed run lists each in-flight amendment with its unit and its reason](../stories/US1187-the-sprint-report-of-a-closed-run-lists.md)

## Acceptance Criteria (Epic Level)

- [ ] `sprint.py batch amend <id> --affects-add <paths> --reason <why>` widens a batch unit's Affects, writes a revision row naming the reason, and records the amendment on the run so the close's report lists it.
- [ ] Narrowing or rewording a criterion of a batch unit goes through the same command (`--criterion ACn --text ...`), and is refused for a unit already reviewed in this run.

> Carried from the request. Author each story's own ACs against its
> slice while grooming - these are the epic's completion bar, not any
> single story's.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-17 | sdlc-studio | Created via `new` (deterministic) |
