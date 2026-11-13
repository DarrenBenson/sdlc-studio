# BG1398: The tool-call budget in a multi-unit lane brief is printed once per unit and nothing states the lane's total

> **Status:** Open
> **Severity:** Low
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_lane_brief_budget.py, .claude/skills/sdlc-studio/scripts/tests/test_lane_total_budget.py, changelog.d/BG1398.md, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py
> **Evidence:** RUN-01M78TKD, 2026-11-13: orchestrator
> **Created:** 2026-11-13
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5 (run eleven orchestrator); agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-13T01:11:20Z

## Summary

The budget line (sprint.py:2867) is printed for each unit, so a builder reading a three-unit brief never sees the lane's sum.

## Steps to Reproduce

Print a brief for a three-unit lane.

## Proposed Fix

Add a total line.

## Acceptance Criteria

- [ ] **AC1** Given a multi-unit lane, when the brief is printed, then it states the lane's total budget once. Fails on: no total.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lane_total_budget.py::LaneTotalBudgetTests

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-13 | Claude Opus 5.5 (run eleven orchestrator) | Filed |
