# EP0133: A correctable review log

> **Status:** Done
> **Derived Point Total:** 5
> **Parent:** CR0372
> **Created:** 2026-07-23
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Size:** M

## Summary

Decomposed from CR0372. Delivers the work CR0372 requested.

## Story Breakdown

- [x] [US0374: critic correct supersedes a verdict row with an authorised reason, the author alone refused](../stories/US0374-critic-correct-supersedes-a-verdict-row-with-an.md)
- [x] [US0375: the sign-off gate ignores a superseded row while it stays visible](../stories/US0375-the-sign-off-gate-ignores-a-superseded-row.md)

## Acceptance Criteria (Epic Level)

- [ ] Given a verdict row that records an event which did not happen, when the operator issues a correction, then the row is superseded through a command rather than a hand edit, and the correction states what was wrong and who authorised it
- [ ] Given a correction has been issued, when the sign-off gate evaluates the unit, then the superseded row no longer disqualifies a principal, while remaining visible in the record
- [ ] Given no correction has been issued, when anyone attempts one, then authorship alone is not sufficient - the author who wrote the wrong row cannot quietly erase it

> Carried from the request. Author each story's own ACs against its
> slice while grooming - these are the epic's completion bar, not any
> single story's.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-23 | sdlc-studio | Created via `new` (deterministic) |
