# EP0358: Windows support for the script tier is stated, tested and safe in its cleanup paths

> **Status:** Draft
> **Derived Point Total:** 8
> **Parent:** CR0719
> **Created:** 2026-11-17
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Size:** M

## Summary

Decomposed from CR0719. Delivers the work CR0719 requested.

## Story Breakdown

- [ ] [US1275: The phase runner's group kill in verify_ac does not raise where killpg or SIGKILL is absent](../stories/US1275-the-phase-runner-s-group-kill-in-verify.md)
- [ ] [US1276: The reap in the mutation runner does not raise where killpg or SIGKILL is absent](../stories/US1276-the-reap-in-the-mutation-runner-does-not.md)
- [ ] [US1277: The Windows smoke job runs a named subset of the script tests and fails when one fails](../stories/US1277-the-windows-smoke-job-runs-a-named-subset.md)
- [ ] [US1278: The TSD states the script tier's supported platforms and the id lock's limit on Windows](../stories/US1278-the-tsd-states-the-script-tier-s-supported.md)

## Acceptance Criteria (Epic Level)

- [ ] The TSD states which platforms the script tier is supported on and, for Windows, either the gate that runs it or an explicit out-of-scope or known-gap entry.
- [ ] If Windows is supported, the `windows-smoke` job runs at least a named subset of the script tests with Python on the Windows runner and fails the job when one fails.
- [ ] The group-kill cleanup in `verify_ac.py` and `mutation.py` does not raise where `os.killpg` or `signal.SIGKILL` is absent, held by a test in each script's test module that removes those attributes and runs the cleanup path.
- [ ] Where the id-allocation lock degrades to no lock, the TSD records it as a stated limit of that platform and does not claim every shared write is serialised there.

> Carried from the request. Author each story's own ACs against its
> slice while grooming - these are the epic's completion bar, not any
> single story's.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-17 | sdlc-studio | Created via `new` (deterministic) |
