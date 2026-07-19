# EP0086: An agent is briefed by the gates before the work, not stopped by them one refusal at a time

> **Status:** Draft
> **Derived Point Total:** 11
> **Parent:** CR0361
> **Created:** 2026-07-19
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Size:** L

## Summary

Decomposed from CR0361. Delivers the work CR0361 requested.

## Story Breakdown

- [ ] [US0266: sprint plan prints the unit lifecycle and the gates each unit will meet, generated from the gate definitions rather than hand-written prose](../stories/US0266-sprint-plan-prints-the-unit-lifecycle-and-the.md)
- [ ] [US0267: A unit close names the fields that unit type requires before its terminal transition, ahead of the work rather than on refusal](../stories/US0267-a-unit-close-names-the-fields-that-unit.md)
- [ ] [US0268: Order the pre-commit lanes cheapest-first so a reworded comment does not cost a full unit-suite run](../stories/US0268-order-the-pre-commit-lanes-cheapest-first-so.md)

## Acceptance Criteria (Epic Level)

- [ ] sprint plan prints the unit lifecycle and the gates each unit will meet, generated from the gate definitions rather than hand-written prose
- [ ] a unit close names the fields that unit type requires before its terminal transition, before the work rather than on refusal
- [ ] the pre-flight has no hand-maintained duplicate of a requirement that already lives in a guard
- [ ] cheap guards (style, artefact fields) run before the unit suites, so a reworded comment does not cost a full test run

> Carried from the request. Author each story's own ACs against its
> slice while grooming - these are the epic's completion bar, not any
> single story's.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-19 | sdlc-studio | Created via `new` (deterministic) |
