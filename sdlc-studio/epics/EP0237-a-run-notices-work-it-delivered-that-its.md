# EP0237: A run notices work it delivered that its batch never named

> **Status:** Draft
> **Derived Point Total:** 8
> **Parent:** CR0546
> **Created:** 2026-08-27
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Size:** M

## Summary

Decomposed from CR0546. Delivers the work CR0546 requested.

## Story Breakdown

- [ ] [US0775: A unit outside the batch reaching terminal is REPORTED, naming the command that would add it](../stories/US0775-a-unit-outside-the-batch-reaching-terminal-is.md)
- [ ] [US0776: A unit IN the batch reaching terminal reports nothing - the prompt must not fire on the normal path](../stories/US0776-a-unit-in-the-batch-reaching-terminal-reports.md)
- [ ] [US0777: The close reports units delivered outside the batch as a non-blocking row naming each id](../stories/US0777-the-close-reports-units-delivered-outside-the-batch.md)

## Acceptance Criteria (Epic Level)

- [ ] Given an open run, when a unit not in its batch reaches a terminal status, then the transition reports it and names the command that would add it
- [ ] Given an open run, when a unit IN its batch reaches a terminal status, then nothing is reported - the prompt must not fire on the normal path
- [ ] Given a run closing with units delivered outside its batch, when the close runs, then it reports them as a non-blocking row naming each id

> Carried from the request. Author each story's own ACs against its
> slice while grooming - these are the epic's completion bar, not any
> single story's.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-27 | sdlc-studio | Created via `new` (deterministic) |
