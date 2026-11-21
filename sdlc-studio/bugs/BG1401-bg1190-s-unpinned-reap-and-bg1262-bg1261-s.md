# BG1401: BG1190's unpinned reap and BG1262/BG1261's watchdog SIGKILL after its grace are covered by no test

> **Status:** Won't Fix
> **Severity:** Low
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/scripts/verify_ac.py, .claude/skills/sdlc-studio/scripts/lib/lanes.py, .claude/skills/sdlc-studio/scripts/tests/test_verify_timeout_reaps.py, .claude/skills/sdlc-studio/scripts/tests/test_reap_after_kill_pin.py, changelog.d/BG1401.md, .claude/skills/sdlc-studio/scripts/tests/test_verify_ac.py
> **Evidence:** RUN-01M78TKD, 2026-11-13: review reaper; review run
> **Created:** 2026-11-13
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5 (run eleven orchestrator); agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-13T01:11:48Z

## Summary

Removing the wait after `verify_ac`'s SIGKILL fallback passes every test, and nothing pins `lanes._watchdog`'s SIGKILL after its grace (lanes.py:761).

## Steps to Reproduce

Delete the wait after SIGKILL; run the suite.

## Proposed Fix

Add the pins.

## Acceptance Criteria

- [ ] **AC1** Given the SIGKILL fallback and the watchdog's grace, when each acts on a SIGTERM-ignoring child, then the child is reaped and killed. Fails on: either wait or kill removed without a failing test.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_reap_after_kill_pin.py::ReapAfterKillPinTests

## Resolution

Won't Fix under D0564: the operator approved the product seat's proposal (D0562) because only a test or pin is missing on behaviour that is right on every path a user reaches. Reap and watchdog SIGKILL behave correctly; only a pin test is absent. No user of the installed skill gains from it. The qa re-check at 81e02369 found the defect still present (D0563), so this closes it as not worth its cost, not as fixed.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-13 | Claude Opus 5.5 (run eleven orchestrator) | Filed |
| 2026-11-21 | Claude Opus 5.5 (product seat, delegate under D0545) | Won't Fix under D0564: the operator approved the product seat's list (D0562); reason in Resolution |
