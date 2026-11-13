# BG1414: The BG1262/BG1261 changelog headline is too broad, the help line reads as SIGTERM-first for every death of sprint.py, and lanes._reaping sends SIGKILL first

> **Status:** Open
> **Severity:** Low
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/scripts/lib/lanes.py, .claude/skills/sdlc-studio/scripts/tests/test_lane_run.py, .claude/skills/sdlc-studio/scripts/tests/test_reaping_order_wording.py, changelog.d/BG1414.md
> **Evidence:** RUN-01M78TKD, 2026-11-13: review run
> **Created:** 2026-11-13
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5 (run eleven orchestrator); agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-13T01:13:27Z

## Summary

The help line is untrue for SIGTERM, SIGINT and SIGHUP (LC-018), and `_reaping` (lanes.py:796) has SIGKILLed first since df67539a, a pre-existing item with no bug.

## Steps to Reproduce

Read the help line and `_reaping`.

## Proposed Fix

Narrow the wording or make `_reaping` SIGTERM-first.

## Acceptance Criteria

- [ ] **AC1** Given the help and changelog text, when read, then they state the SIGKILL-first cases. Fails on: SIGTERM-first stated for all deaths.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_reaping_order_wording.py::ReapingOrderWordingTests

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-13 | Claude Opus 5.5 (run eleven orchestrator) | Filed |
