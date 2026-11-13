# BG1406: lane run accepts a home-isolated unit and hands its worktree builder the main-checkout brief, and 'Isolation: no home' reads as home

> **Status:** Open
> **Severity:** Medium
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_lane_run.py, .claude/skills/sdlc-studio/scripts/tests/test_home_isolation_lane_run.py, changelog.d/BG1406.md, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py
> **Evidence:** RUN-01M78TKD, 2026-11-13: lane accept builder; review accept
> **Created:** 2026-11-13
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5 (run eleven orchestrator); agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-13T01:12:27Z

## Summary

BG1344 covered only the brief. `lane run` still runs an `Isolation: home` unit in a worktree, and `LANE_ISOLATION_FIELD` (sprint.py:2807, 2872) reads 'no home' as home.

## Steps to Reproduce

lane run a home-isolated unit.

## Proposed Fix

Refuse it and parse the value exactly.

## Acceptance Criteria

- [ ] **AC1** Given a unit with Isolation: home, when `lane run` selects it, then it refuses or runs it in the main checkout, and 'no home' is not home. Fails on: a worktree run.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_home_isolation_lane_run.py::HomeIsolationLaneRunTests

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-13 | Claude Opus 5.5 (run eleven orchestrator) | Filed |
