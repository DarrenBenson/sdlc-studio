# BG1403: retro's new `supplied` guard and its `declined` list have no tests

> **Status:** Open
> **Severity:** Low
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/scripts/retro.py, .claude/skills/sdlc-studio/scripts/tests/test_retro.py, .claude/skills/sdlc-studio/scripts/tests/test_supplied_guard_and_declined.py, changelog.d/BG1403.md
> **Evidence:** RUN-01M78TKD, 2026-11-13: review upgrade, BG1371 and BG0965
> **Created:** 2026-11-13
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5 (run eleven orchestrator); agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-13T01:12:04Z

## Summary

No test covers the `supplied` half of the BG1371 guard (retro.py:2273), and none checks what goes into retro's `declined` list (pre-existing, BG0965).

## Steps to Reproduce

Mutate the guard at retro.py:2273.

## Proposed Fix

Add both tests.

## Acceptance Criteria

- [ ] **AC1** Given supplied totals and declined actions, when retro runs, then the guard and declined list are as stated. Fails on: either half changed with the suite green.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_supplied_guard_and_declined.py::SuppliedGuardAndDeclinedTests

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-13 | Claude Opus 5.5 (run eleven orchestrator) | Filed |
