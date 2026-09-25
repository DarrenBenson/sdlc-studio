# BG0781: A busy lock reported as EACCES fails at once, and two lock warnings advise a retry that duplicates

> **Status:** Open
> **Severity:** Medium
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/lib/sdlc_md.py, .claude/skills/sdlc-studio/scripts/file_finding.py, .claude/skills/sdlc-studio/scripts/critic.py, .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_sdlc_md.py, .claude/skills/sdlc-studio/scripts/tests/test_file_finding.py, .claude/skills/sdlc-studio/scripts/tests/test_critic.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py
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

- [ ] **AC1** The behaviour described is corrected: After BG0780: (1) `allocation_lock` waits only on BlockingIOError, so a filesystem reporting a busy flock as EACCES (SMB without unix extensions) fails at once...
- [ ] **AC2** Following the recorded steps no longer reproduces the defect: Fake flock busy-as-EACCES three times then free: base waits and takes the lock, HEAD fails at once.
- [ ] **AC3** The proposed fix lands, pinned by a test: Treat EACCES as busy with a control case; phrase the two warnings without the timeout's remedy, naming how to remove a stranded row; report a non-busy flock...

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-25 | sdlc-studio | Filed |
