# BG0753: The test suite leaks temporary directories into /tmp

> **Status:** Open
> **Severity:** Medium
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/tests
> **Evidence:** RUN-01M3891F: /tmp at 1048576/1048576 inodes; lane B commit failed with 32 ENOSPC errors
> **Created:** 2026-09-24
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

Test runs leave `tmp*` directories behind: about 44,000 were seen in one sprint, and /tmp ran out of inodes mid-run, failing a commit's suites with ENOSPC (Errno 28).

## Steps to Reproduce

1. Run `bash tools/skill-tests.sh` several times. 2. `ls -d /tmp/tmp* | wc -l` grows each run.

## Proposed Fix

Find the fixtures that create temp dirs without cleanup (mkdtemp with no rmtree, TemporaryDirectory not closed) and add a leak check to the suite.

## Acceptance Criteria

- [ ] **AC1** The behaviour described is corrected: Test runs leave `tmp*` directories behind: about 44,000 were seen in one sprint, and /tmp ran out of inodes mid-run, failing a commit's suites with ENOSPC...
- [ ] **AC2** The proposed fix lands, pinned by a test: Find the fixtures that create temp dirs without cleanup (mkdtemp with no rmtree, TemporaryDirectory not closed) and add a leak check to the suite.

## Impact

Test runs leave `tmp*` directories behind: about 44,000 were seen in one sprint, and /tmp ran out of inodes mid-run, failing a commit's suites with ENOSPC (Errno 28).

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-24 | sdlc-studio | Filed |
