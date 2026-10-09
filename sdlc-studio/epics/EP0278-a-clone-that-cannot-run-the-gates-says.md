# EP0278: A clone that cannot run the gates says so at setup and at the push, in seconds

> **Status:** Draft
> **Derived Point Total:** 10
> **Parent:** CR0613
> **Created:** 2026-10-09
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Size:** L

## Summary

Decomposed from CR0613. Delivers the work CR0613 requested.

## Story Breakdown

- [ ] [US1003: enable-hooks.sh names every missing gate prerequisite with a route that works on this interpreter](../stories/US1003-enable-hooks-sh-names-every-missing-gate-prerequisite.md)
- [ ] [US1004: CI and the checker read one list of suite prerequisites](../stories/US1004-ci-and-the-checker-read-one-list-of.md)
- [ ] [US1005: The pre-push hook refuses in seconds, before the suite, when the suite cannot be green on this interpreter](../stories/US1005-the-pre-push-hook-refuses-in-seconds-before.md)
- [ ] [US1006: The push's first-run cost line says what it does not know instead of a fixed five minutes](../stories/US1006-the-push-s-first-run-cost-line-says.md)

## Acceptance Criteria (Epic Level)

- [ ] `enable-hooks.sh` names each missing gate prerequisite (pytest, pytest-xdist, coverage, markdownlint, gh) with the command that installs it
- [ ] A session can tell in one command that a clone's hooks are off
- [ ] The pre-push gate refuses in seconds, before the suite, when a prerequisite it needs is missing, and its first-run estimate is not a fixed five minutes

> Carried from the request. Author each story's own ACs against its
> slice while grooming - these are the epic's completion bar, not any
> single story's.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-09 | sdlc-studio | Created via `new` (deterministic) |
