# EP0144: Installed-copy drift detection

> **Status:** Done
> **Derived Point Total:** 6
> **Parent:** CR0389
> **Created:** 2026-07-23
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Size:** M

## Summary

Decomposed from CR0389. Delivers the work CR0389 requested.

## Story Breakdown

- [x] [US0388: a forward-port drift check exits non-zero with a differing-file count, handling no copy and a pinned copy](../stories/US0388-a-forward-port-drift-check-exits-non-zero.md)
- [x] [US0389: surface the drift in the status hint and the close chain](../stories/US0389-surface-the-drift-in-the-status-hint-and.md)

## Acceptance Criteria (Epic Level)

- [ ] A drift check exists that exits non-zero when the installed copy differs from the repo skill tree, and names the count of differing files rather than only listing them.
- [ ] The check is surfaced somewhere the operator or agent already looks - `status hint` and/or the sprint close chain - rather than in a command that must be remembered.
- [ ] A machine with no installed copy, or one deliberately pinned, is reported as such and does not fail the check.

> Carried from the request. Author each story's own ACs against its
> slice while grooming - these are the epic's completion bar, not any
> single story's.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-23 | sdlc-studio | Created via `new` (deterministic) |
