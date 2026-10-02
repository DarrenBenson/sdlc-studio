# BG0899: A lane brief reopens the span of a unit already at a terminal status

> **Status:** In Progress
> **Severity:** Low
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_lean_lane_rebrief_terminal.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py
> **Evidence:** US0979 QA review (RUN-01M3Y7DP)
> **Created:** 2026-10-02
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-10-02T12:28:38Z

## Summary

Since US0979, sprint lane brief opens a span for every briefed unit whatever its status (sprint.py:8510-8517). A plain lane brief with no --units briefs the whole batch, so a unit already Done and measured gets a new open span, and if that lane never returns the page reads NOT MEASURED where it read the measured minutes.

## Steps to Reproduce

1. A unit In Progress at T0 and Done at T+10. 2. sprint lane brief (no --units) at T+15. 3. sprint close at T+20 -> NOT MEASURED, base read 10.0 min.

## Proposed Fix

Open a span on brief only for a unit not yet at a terminal status.

## Acceptance Criteria

- [ ] **AC1** Given a unit that reached Done with a closed 10-minute span, when sprint lane brief briefs the whole batch and the run closes, then the unit still reads 10.0 minutes and no span is reopened. Fails on: the current code reopens the span and reads NOT MEASURED
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_lane_rebrief_terminal.py::LaneRebriefTerminalTests::test_a_brief_leaves_a_terminal_unit_measured
  - **Verified:** yes (2026-10-02)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-02 | sdlc-studio | Filed |
