# CR-0711: Show each open lane's liveness, so a stalled builder is caught in minutes rather than hours

> **Status:** Proposed
> **Priority:** Medium
> **Type:** Feature
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint_lane.py, .claude/skills/sdlc-studio/reference-sprint-toolchain.md, changelog.d/CR0711.md, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py
> **Evidence:** Run fourteen (RUN-01M7GEHM) sweep lane, 2026-11-15/16.
> **Date:** 2026-11-16
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-16T01:57:47Z

## Summary

In run fourteen, the sweep lane's builder stalled for 2 h 10 min: it wrote no file and made no tool call that could receive a status message. The orchestrator found out only by checking the worktree by hand. The toolchain offers no per-lane liveness view (a worktree's last change, the builder's last tool round, elapsed against the lane's estimate), so a stall costs the run its wall-clock.

## Acceptance Criteria

_None yet: add them here, or on the stories `refine` decomposes this into._

## Proposed Fix

Add `sprint.py lane status`: for each open lane, print its worktree path, the age of its newest changed file, its elapsed time against the lane's points-based estimate, and a STALLED mark past a configurable threshold with no change.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-16 | sdlc-studio | Raised |
