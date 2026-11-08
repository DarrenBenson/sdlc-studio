# BG1283: One old Codex thread whose rollout file is gone makes every later Codex reading in that workspace unmetered, permanently

> **Status:** Open
> **Severity:** Low
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/lib/meter_codex.py, .claude/skills/sdlc-studio/scripts/tests/test_meter_codex.py
> **Evidence:** the between-releases review before v6.3.0 (D0427, LL0005), code leg A; repro under scratchpad rel63/legs/scratch-a/
> **Created:** 2026-11-08
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-08T13:07:10Z

## Summary

Every Codex reading folds every workspace thread ever recorded. One old thread whose rollout file was pruned or moved therefore makes every later reading in that workspace tokens None, permanently, though that thread is no part of any later run. Each reading also re-reads every historical rollout in full.

## Steps to Reproduce

by reading: `_usage` returns 'is missing' and read() returns none(...) for any thread with `tokens_used` truthy (not executed).

## Proposed Fix

Skip and count a thread whose rollout is missing and which has not changed since the run opened (or since the previous stamp), and name it in the basis.

## Acceptance Criteria

- [ ] **AC1** The behaviour described is corrected: Every Codex reading folds every workspace thread ever recorded.
- [ ] **AC2** Following the recorded steps no longer reproduces the defect: by reading: `_usage` returns 'is missing' and read() returns none(...) for any thread with `tokens_used` truthy (not executed).
- [ ] **AC3** The proposed fix lands, pinned by a test: Skip and count a thread whose rollout is missing and which has not changed since the run opened (or since the previous stamp), and name it in the basis.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-08 | Claude Opus 5.5 | Filed |
