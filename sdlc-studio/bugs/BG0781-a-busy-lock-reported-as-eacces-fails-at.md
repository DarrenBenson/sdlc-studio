# BG0781: A busy lock reported as EACCES fails at once, and two lock warnings advise a retry that duplicates

> **Status:** Open
> **Severity:** Medium
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/lib/sdlc_md.py, .claude/skills/sdlc-studio/scripts/file_finding.py, .claude/skills/sdlc-studio/scripts/critic.py, .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_lean_lock_busy_eacces.py, changelog.d/BG0781.md
> **Created:** 2026-09-25
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-09-25T19:41:35Z

## Summary

After BG0780: (1) `allocation_lock` waits only on BlockingIOError, so a filesystem reporting a busy flock as EACCES (SMB without unix extensions) fails at once as Permission denied where base waited; (2) `file_finding`'s attribution warning and critic's stranded-row error append the timeout's remedy 'so nothing was written; retry once it finishes', but the finding was filed (a retry mints a duplicate) and the provisional row still stands; (3) a non-busy flock OSError still escapes sprint.main as a traceback. Found by BG0780's QA review.

## Steps to Reproduce

Fake flock busy-as-EACCES three times then free: base waits and takes the lock, HEAD fails at once.

## Proposed Fix

Treat EACCES as busy with a control case; phrase the two warnings without the timeout's remedy, naming how to remove a stranded row; report a non-busy flock error from sprint.main as one error line.

## Acceptance Criteria

- [ ] **AC1** Given `fcntl.flock` reporting a busy lock as EACCES a few times and then succeeding, when a writer takes the allocation lock, then it waits and takes it, as it does for `BlockingIOError`; a non-busy errno such as ENOLCK still fails at once. Fails on: waiting only on `BlockingIOError`
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_lock_busy_eacces.py::LockBusyEaccesTests::test_a_busy_lock_reported_as_eacces_is_waited_on
- [ ] **AC2** Given the lock held past the timeout, when `file_finding.py file` warns that it could not attribute the filing to the batch, or `critic.provisional_verdict` reports a stranded row, then neither message advises a retry or says nothing was written, and the stranded-row message names how to remove the row. Fails on: appending the timeout's generic remedy
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_lock_busy_eacces.py::LockBusyEaccesTests::test_the_lock_warnings_do_not_advise_a_retry
- [ ] **AC3** Given a non-busy flock error during a `sprint.py` verb, then it prints one `error:` line naming the errno and exits non-zero, with no traceback. Fails on: catching only `AllocationLockTimeout` in `sprint.main`
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_lock_busy_eacces.py::LockBusyEaccesTests::test_a_non_busy_flock_error_is_one_line_from_sprint

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-25 | sdlc-studio | Filed |
| 2026-09-25 | sdlc | Groomed for Sprint 5: criteria and Verify selectors written |
