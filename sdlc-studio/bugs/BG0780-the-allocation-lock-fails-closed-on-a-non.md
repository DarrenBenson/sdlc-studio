# BG0780: The allocation lock fails closed on a non-busy flock error, and three callers mishandle its timeout

> **Status:** Fixed
> **Severity:** Medium
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/lib/sdlc_md.py, .claude/skills/sdlc-studio/scripts/critic.py, .claude/skills/sdlc-studio/scripts/file_finding.py, .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_lean_lock_errors.py, changelog.d/BG0780.md
> **Created:** 2026-09-25
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-09-25T19:16:10Z

## Summary

US0948 made `allocation_lock` raise AllocationLockTimeout. Its QA review found: (1) any OSError from flock, e.g. ENOLCK on NFS with no lock daemon, is retried and then reported as another writer holding the lock, so every write fails where base proceeded; (2) `critic.provisional_verdict`'s withdrawal (critic.py:446) under a lock held over 10s raises, leaving the provisional APPROVE row behind and dropping the gate's real refusal; (3) `file_finding._attribute_to_open_batch` and sprint.py `stamp_tokens` swallow the timeout into a debug log while the CLI prints success; (4) sprint.py run-state writers print a raw traceback rather than an error line.

## Steps to Reproduce

1. Monkeypatch fcntl.flock to raise OSError(ENOLCK); run decisions.py add: it fails after 10s naming another writer. 2. Hold the lock over 10s while a transition refuses a provisional verdict: the row stays.

## Proposed Fix

Retry only on BlockingIOError and report the real errno otherwise; catch the timeout in the provisional withdrawal and report both the stale row and the original refusal; warn on stderr in the two swallowers; report the timeout as one error line in sprint.py.

## Acceptance Criteria

- [ ] **AC1** Given `fcntl.flock` raising an `OSError` other than a busy lock (ENOLCK), when a writer takes the allocation lock, then it fails at once with an error naming that errno, without waiting out the timeout or claiming another writer holds it. Fails on: retrying every `OSError` as if the lock were busy
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_lock_errors.py::LockErrorTests::test_a_non_busy_flock_error_is_named_at_once
  - **Verified:** yes (2026-09-25)
- [ ] **AC2** Given a provisional verdict whose transition is refused while another process holds the lock past the timeout, when `critic.provisional_verdict` withdraws it, then the command exits non-zero naming both the transition's refusal and the provisional row it could not withdraw. Fails on: raising the timeout alone, which drops the refusal and says nothing was written
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_lock_errors.py::LockErrorTests::test_a_stranded_provisional_row_is_named_with_the_refusal
  - **Verified:** yes (2026-09-25)
- [ ] **AC3** Given the lock held past the timeout, when `file_finding.py file` attributes a finding to the open batch, or `sprint.py` stamps tokens, then a warning naming the lock goes to stderr while the primary write stands. Fails on: the timeout swallowed into a debug log only
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_lock_errors.py::LockErrorTests::test_a_swallowed_timeout_warns_on_stderr
  - **Verified:** yes (2026-09-25)
- [ ] **AC4** Given the lock held past the timeout, when a `sprint.py` verb that writes run state runs, then it prints one `error:` line naming the lock and exits non-zero, with no traceback. Fails on: letting `AllocationLockTimeout` escape as a traceback
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_lock_errors.py::LockErrorTests::test_a_sprint_writer_reports_the_timeout_in_one_line
  - **Verified:** yes (2026-09-25)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-25 | sdlc-studio | Filed |
| 2026-09-25 | sdlc | Groomed for Sprint 5: criteria and Verify selectors written |
