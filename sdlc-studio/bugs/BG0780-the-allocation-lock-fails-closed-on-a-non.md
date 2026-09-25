# BG0780: The allocation lock fails closed on a non-busy flock error, and three callers mishandle its timeout

> **Status:** Open
> **Severity:** Medium
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/lib/sdlc_md.py, .claude/skills/sdlc-studio/scripts/critic.py, .claude/skills/sdlc-studio/scripts/file_finding.py, .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_sdlc_md.py, .claude/skills/sdlc-studio/scripts/tests/test_critic.py, .claude/skills/sdlc-studio/scripts/tests/test_file_finding.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py
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

- [ ] **AC1** The behaviour described is corrected: US0948 made `allocation_lock` raise AllocationLockTimeout.
- [ ] **AC2** The proposed fix lands, pinned by a test: Retry only on BlockingIOError and report the real errno otherwise; catch the timeout in the provisional withdrawal and report both the stale row and the...

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-25 | sdlc-studio | Filed |
