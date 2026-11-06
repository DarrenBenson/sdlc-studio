# BG1272: The pre-push check reads only the latest Lint run, so a push made while the previous run is still in progress never sees it fail

> **Status:** Open
> **Severity:** Medium
> **Points:** 2
> **Affects:** .githooks/pre-push, tools/tests/test_pre_push_red_main.py
> **Evidence:** run eight (RUN-01M6RZQZ) mid-run push, GitHub Actions Lint run 42263229398
> **Created:** 2026-11-06
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-06T20:38:52Z

## Summary

The forge's Lint job failed on main at 8a00d2cc, fb93b20d and fd1c2b5b (BG1259) and the pre-push hook let each later push through, because every push left while the previous 45-minute run was still in progress; the hook reads the latest push-triggered run, and an unfinished one is not a red. The red was first read at run eight's mid-run push.

## Steps to Reproduce

Push, then push again within the CI run's duration while it is failing; the second push is not refused.

## Proposed Fix

When the latest run on main is in progress, read the most recent concluded run as well, or name the in-progress run and the parent commit it judges, so a red parent is never silently skipped.

## Acceptance Criteria

- [ ] **AC1** The behaviour described is corrected: The forge's Lint job failed on main at 8a00d2cc, fb93b20d and fd1c2b5b (BG1259) and the pre-push hook let each later push through, because every push left...
- [ ] **AC2** Following the recorded steps no longer reproduces the defect: Push, then push again within the CI run's duration while it is failing; the second push is not refused.
- [ ] **AC3** The proposed fix lands, pinned by a test: When the latest run on main is in progress, read the most recent concluded run as well, or name the in-progress run and the parent commit it judges, so a red...

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-06 | Claude Opus 5.5 | Filed |
