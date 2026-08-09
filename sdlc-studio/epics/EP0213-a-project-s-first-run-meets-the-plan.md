# EP0213: A project's first run meets the plan-review gate as a report, and every run after it as a refusal

> **Status:** Draft
> **Derived Point Total:** 8
> **Parent:** CR0541
> **Created:** 2026-08-09
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Size:** M

## Summary

Decomposed from CR0541. Delivers the work CR0541 requested.

## Story Breakdown

- [ ] [US0662: A project with no closed run reports the plan-review requirement at the terminal transition instead of refusing, and names the condition that arms it](../stories/US0662-a-project-with-no-closed-run-reports-the.md)
- [ ] [US0663: The softening expires on run history alone, so a second run refuses and an upgrading project is unaffected byte-for-byte](../stories/US0663-the-softening-expires-on-run-history-alone-so.md)

## Acceptance Criteria (Epic Level)

- [ ] A project with no closed run reports the plan-review requirement at the terminal transition and does not refuse, proven through the shipped `transition.py` on a greenfield fixture built by `init run`
- [ ] The same project's SECOND run refuses on the same story shape, proving the softening expires rather than persists (positive control on the same fixture, run history the only difference)
- [ ] A project that already has run history - the upgrading case - is unaffected byte-for-byte, and the test asserts the output is identical to the current behaviour
- [ ] The first-run report names the condition that arms the gate, and a test pins that the condition named is the one the gate actually reads rather than a restatement of it

> Carried from the request. Author each story's own ACs against its
> slice while grooming - these are the epic's completion bar, not any
> single story's.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-09 | sdlc-studio | Created via `new` (deterministic) |
