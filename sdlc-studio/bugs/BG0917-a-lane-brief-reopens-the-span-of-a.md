# BG0917: A lane brief reopens the span of a bug already at Fixed or Verified

> **Status:** In Progress
> **Severity:** Low
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_lean_lane_rebrief_terminal_bug.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py
> **Created:** 2026-10-03
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-10-02T23:47:04Z

## Summary

BG0899 skips reopening a span only for status Done; a bug at Fixed or Verified (also terminal) still has its span reopened by a later lane brief, so its measured minutes read NOT MEASURED. The reviewer's mutant status == 'Done' survived the suite.

## Steps to Reproduce

1. A bug at Fixed whose lane returned. 2. sprint lane brief --units it. 3. The page reads NOT MEASURED for it.

## Proposed Fix

Test the shared terminal-status set, not Done alone. No new refusal.

## Acceptance Criteria

- [ ] **AC1** Given a bug at Fixed whose lane returned 10 minutes, when a lane brief names it again, then its span stays closed and the page reads 10.0. Fails on: a check against Done alone
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_lane_rebrief_terminal_bug.py::LaneRebriefTerminalBugTests::test_a_fixed_bug_keeps_its_span

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-03 | sdlc-studio | Filed |
