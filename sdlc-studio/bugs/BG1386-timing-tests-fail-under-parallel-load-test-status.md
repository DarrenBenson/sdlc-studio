# BG1386: Timing tests fail under parallel load: test_status GatherPerformanceTests read 4.9 s against a 3 s limit and a verify_ac criterion failed once at load 8.6

> **Status:** Open
> **Severity:** Low
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/scripts/status.py, .claude/skills/sdlc-studio/scripts/tests/test_status.py, .claude/skills/sdlc-studio/scripts/tests/test_gather_performance_load.py, changelog.d/BG1386.md
> **Evidence:** RUN-01M78TKD, 2026-11-13: lane upgrade builder; lane verify builder
> **Created:** 2026-11-13
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5 (run eleven orchestrator); agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-13T01:07:35Z

## Summary

GatherPerformanceTests (`test_status.py`:1200) asserts a 3 s limit that read 4.9 s while parallel lanes ran. BG1005's AC2 also failed once (exit 1, no output) at load about 8.6 and then passed 13 times.

## Steps to Reproduce

Run the module while three lanes run tests.

## Proposed Fix

Measure CPU time or operation counts, or scale the limit by load.

## Acceptance Criteria

- [ ] **AC1** Given a machine under parallel-lane load, when the status gather performance test runs, then it judges work done rather than wall-clock seconds. Fails on: a pass or fail that depends on machine load.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_gather_performance_load.py::GatherPerformanceLoadTests

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-13 | Claude Opus 5.5 (run eleven orchestrator) | Filed |
