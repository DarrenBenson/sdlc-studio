# EP0340: After a push the agent waits on CI once and handles a red run by a recorded policy

> **Status:** Draft
> **Derived Point Total:** 9
> **Parent:** CR0697
> **Created:** 2026-11-17
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Size:** L

## Summary

Decomposed from CR0697. Delivers the work CR0697 requested.

## Story Breakdown

- [ ] [US1236: The trunk guidance tells the agent to wait on its CI run with one blocking watch and to read a red main first](../stories/US1236-the-trunk-guidance-tells-the-agent-to-wait.md)
- [ ] [US1237: A project sets the CI wait timeout and the rerun limit in config, with the defaults documented](../stories/US1237-a-project-sets-the-ci-wait-timeout-and.md)
- [ ] [US1238: A red CI run is recorded against its filed flaky bug and rerun once, or filed as a regression holding pushes](../stories/US1238-a-red-ci-run-is-recorded-against-its.md)

## Acceptance Criteria (Epic Level)

- [ ] The shipped trunk guidance tells the agent to wait on its push's CI run with one blocking command under a timeout (for GitHub, `gh run watch <id> --exit-status`), never a polling loop, and to read a red main before pushing again
- [ ] A red run whose failing test is already filed as a flaky bug is recorded against that bug; the agent reruns the failed jobs once when its token allows it, or else stops and asks the operator to rerun, and never skips the test
- [ ] A red run that matches no filed flake is treated as a regression: the agent files a bug and does not push again until main is green
- [ ] A project can set the wait's timeout and the rerun limit (default one) in its config, and the defaults are documented in reference-config.md

> Carried from the request. Author each story's own ACs against its
> slice while grooming - these are the epic's completion bar, not any
> single story's.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-17 | sdlc-studio | Created via `new` (deterministic) |
