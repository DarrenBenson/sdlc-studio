# BG0754: A commit touching a widely imported script runs well over the 90-second budget

> **Status:** Open
> **Severity:** Medium
> **Points:** 5
> **Affects:** .claude/skills/sdlc-studio/scripts/tests/test_sprint.py
> **Evidence:** US0880 hand-back and commit 315ec358 (247s), RUN-01M3891F
> **Created:** 2026-09-24
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

US0880 reports the commit's time against 90s and never refuses. A change to gate.py or sprint.py selects the modules that import it, and `test_sprint.py` alone takes about 50s, so such a commit took 218-390s under load (US0880's own: 247s).

## Steps to Reproduce

1. Change `gate.py`. 2. Commit. 3. The hook prints `over budget ... reported, not refused`.

## Proposed Fix

Split `test_sprint.py` and the other slow hub modules so a direct-edge selection stays under 90s.

## Acceptance Criteria

- [ ] **AC1** The behaviour described is corrected: US0880 reports the commit's time against 90s and never refuses.
- [ ] **AC2** The proposed fix lands, pinned by a test: Split `test_sprint.py` and the other slow hub modules so a direct-edge selection stays under 90s.

## Impact

US0880 reports the commit's time against 90s and never refuses.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-24 | sdlc-studio | Filed |
