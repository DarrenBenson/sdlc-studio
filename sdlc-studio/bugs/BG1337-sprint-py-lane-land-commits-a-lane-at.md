# BG1337: sprint.py lane land commits a lane at its worktree's old base and rebases afterwards, so the hook judges it against code main has already fixed

> **Status:** Fixed
> **Severity:** Medium
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/lib/lanes.py, .claude/skills/sdlc-studio/scripts/tests/test_lane_land.py, changelog.d/BG1337.md
> **Evidence:** RUN-01M77177, 2026-11-12: US1000 refused after BG1334 landed
> **Created:** 2026-11-12
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5 (run ten orchestrator); agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-12T13:18:37Z

## Summary

`lane land` commits through the hooks inside the lane's worktree, at the base the builder started from, and only then rebases onto main. When main fixed a red test in the meantime, the lane's commit hook still runs the old code and refuses the land for a failure main no longer has.

## Steps to Reproduce

Start a lane, land a fix to a red test on main, then land the lane: its commit hook fails on the fixed test (US1000 after BG1334).

## Proposed Fix

Fast-forward or rebase the worktree onto main before the commit, holding the staged work across it.

## Acceptance Criteria

- [ ] **AC1** Given a lane worktree behind main, where main fixed a test that fails at the worktree's base, when `sprint lane land` runs, then the commit hook judges the lane on main's code and the land succeeds. Fails on: the land refused for a failure present only at the old base.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lane_land.py::LaneLandTests::test_a_lane_behind_main_is_judged_on_mains_code
  - **Verified:** yes (2026-11-13)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-12 | Claude Opus 5.5 (run ten orchestrator) | Filed |
