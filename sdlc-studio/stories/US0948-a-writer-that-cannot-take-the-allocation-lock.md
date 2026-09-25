# US0948: A writer that cannot take the allocation lock writes nothing instead of losing rows

> **Status:** Draft
> **Created:** 2026-09-25
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/lib/sdlc_md.py, .claude/skills/sdlc-studio/scripts/tests/test_lean_lock_fails_closed.py, changelog.d/US0948.md
> **Epic:** EP0265
> **Points:** 2
> **Persona:** Maya Okafor

## User Story

**As a** founder-engineer running several review lanes at once
**I want** `sdlc_md.allocation_lock` to fail with a named error when it cannot take the lock in time, rather than proceed without it
**So that** concurrent verdicts, ids and decisions are never silently lost (39 of 65 concurrent verdict rows were lost with the lock held 12 seconds)

## Acceptance Criteria

- **AC1:** Given the lock held by another process past the timeout, when a second writer enters `allocation_lock`, then it raises an error naming the lock file and the holder's wait, and the writer's file is unchanged. Fails on: HEAD, which breaks out of the wait loop and yields without the lock (`sdlc_md.py`:2330-2333)
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_lock_fails_closed.py::LockFailsClosedTests::test_a_timed_out_writer_writes_nothing
- **AC2:** Given 20 processes each appending one row under the lock while each holds it briefly, then the file holds all 20 rows. Fails on: a longer timeout that still yields without the lock once it expires
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_lock_fails_closed.py::LockFailsClosedTests::test_concurrent_writers_lose_no_row
- **AC3:** Given a holder process killed while holding the lock, when a new writer enters, then it takes the lock at once. Fails on: replacing flock with a PID or marker file, which a killed holder leaves behind and which is the stale-lock case the old fail-open existed to avoid
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_lock_fails_closed.py::LockFailsClosedTests::test_a_killed_holder_does_not_wedge_the_next_writer

## Notes

From CR0592 (US0873 review probe). flock locks are released by the kernel when the holder dies, so failing closed cannot wedge an agent wave; the docstring's reason for failing open does not apply to flock. The non-POSIX no-op branch stays. Callers (artifact.py, decisions.py, file_finding.py, critic.py, run_state.py) surface the error as their existing non-zero exit; no caller change is needed beyond that, so they are not in Affects unless a caller swallows the exception.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-25 | sdlc-studio v6 planning | Created for v6.0.0 Sprint 5 from the seat planning (N10) |
