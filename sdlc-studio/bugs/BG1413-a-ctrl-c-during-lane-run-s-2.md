# BG1413: A Ctrl-C during lane run's 2 s kill grace drops the SIGKILL that follows, so a SIGTERM-ignoring child stages after the run, and nothing pins that SIGKILL

> **Status:** Open
> **Severity:** Medium
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/lib/lanes.py, .claude/skills/sdlc-studio/scripts/tests/test_lane_run.py, .claude/skills/sdlc-studio/scripts/tests/test_kill_grace_interrupt.py, changelog.d/BG1413.md
> **Evidence:** RUN-01M78TKD, 2026-11-13: review run
> **Created:** 2026-11-13
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5 (run eleven orchestrator); agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-13T01:13:19Z

## Summary

A regression ruled non-blocking in lanes.py (the kill grace near line 690).

## Steps to Reproduce

Start a lane with a SIGTERM-ignoring child, Ctrl-C twice.

## Proposed Fix

Make the SIGKILL unconditional in a finally.

## Acceptance Criteria

- [ ] **AC1** Given a child ignoring SIGTERM and a Ctrl-C in the grace, when lane run exits, then the child is SIGKILLed. Fails on: the child alive.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_kill_grace_interrupt.py::KillGraceInterruptTests

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-13 | Claude Opus 5.5 (run eleven orchestrator) | Filed |
