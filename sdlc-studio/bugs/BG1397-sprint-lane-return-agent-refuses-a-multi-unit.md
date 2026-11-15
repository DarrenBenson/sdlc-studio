# BG1397: sprint lane return --agent refuses a multi-unit lane, so a multi-unit lane's builder is never priced per unit

> **Status:** Fixed
> **Severity:** Medium
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_lane_priced.py, .claude/skills/sdlc-studio/scripts/tests/test_multi_unit_lane_split.py, changelog.d/BG1397.md, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py, .claude/skills/sdlc-studio/scripts/sprint_report.py, .claude/skills/sdlc-studio/scripts/lib/run_state.py, .claude/skills/sdlc-studio/scripts/tests/test_lane_land.py, .claude/skills/sdlc-studio/scripts/tests/test_lean_lane_delegated_tokens.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py, .claude/skills/sdlc-studio/scripts/tests/test_run_state.py
> **Evidence:** RUN-01M78TKD, 2026-11-13: orchestrator
> **Created:** 2026-11-13
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5 (run eleven orchestrator); agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-13T01:11:10Z

## Summary

sprint.py:8615 says 'one total cannot be split between N units', so every multi-unit lane in run eleven went unpriced per unit. It could split by points and say so.

## Steps to Reproduce

`sprint lane return --agent A` on a three-unit lane.

## Proposed Fix

Split by points and mark the figure as apportioned.

## Acceptance Criteria

- [ ] **AC1** Given a lane of three units and one agent total, when `sprint lane return --agent` runs, then the total is split by points, each unit is priced and the page says it was split. Fails on: the refusal.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_multi_unit_lane_split.py::MultiUnitLaneSplitTests
  - **Verified:** yes (2026-11-15)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-13 | Claude Opus 5.5 (run eleven orchestrator) | Filed |
| 2026-11-14 | Claude Opus 5.5 (run twelve) | Affects widened: the criterion's page text is written by sprint_report.py, so the fix lives there too, and the tests that pin the current multi-unit refusal move with it (the builder's BLOCKED hand-back) |
