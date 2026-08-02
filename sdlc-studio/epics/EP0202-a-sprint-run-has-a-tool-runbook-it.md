# EP0202: A sprint run has a tool runbook it is made to read, ordered by step rather than by script

> **Status:** Draft
> **Derived Point Total:** 10
> **Parent:** CR0518
> **Created:** 2026-08-01
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Size:** L

## Summary

Decomposed from CR0518. Delivers the work CR0518 requested.

## Story Breakdown

- [x] [US0612: A runbook ordered by SPRINT STEP names the one command that performs each step, its fields-file path, and the hand-rolled shape it replaces](../stories/US0612-a-runbook-ordered-by-sprint-step-names-the.md)
- [x] [US0613: sprint plan and sprint run PRINT the runbook, and a guard fails when a step names a command that no longer exists](../stories/US0613-sprint-plan-and-sprint-run-print-the-runbook.md)

## Acceptance Criteria (Epic Level)

- [ ] A runbook exists ordered by sprint STEP, not by script, covering plan, groom, batch,
- [ ] Each step names the hand-rolled shape it replaces, so the entry is recognisable from
- [ ] `sprint plan` and `sprint run` print the runbook, so it reaches the agent at the step
- [ ] A guard fails when a step in the runbook names a command that no longer exists, so the
- [ ] The runbook is derived from the shipped command surface where it can be, not restated

> Carried from the request. Author each story's own ACs against its
> slice while grooming - these are the epic's completion bar, not any
> single story's.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-01 | sdlc-studio | Created via `new` (deterministic) |
