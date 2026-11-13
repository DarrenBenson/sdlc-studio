# BG1344: A unit whose tests must run under a temporary HOME cannot be built in a worktree lane, and the lane brief offers no other path

> **Status:** Fixed
> **Severity:** Medium
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/help/sprint.md, .claude/skills/sdlc-studio/scripts/tests/test_lean_brief_handover.py, changelog.d/BG1344.md, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py
> **Evidence:** RUN-01M77177, 2026-11-12: BG1300 refused twice (run nine and run ten)
> **Created:** 2026-11-12
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5 (run ten orchestrator); agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-12T13:19:18Z

## Summary

Claude Code's worktree command-shape check refuses `HOME=$(mktemp -d) python3 -m pytest ...` and `git -C <other worktree>`, and its documentation says the check cannot be turned off; an allow rule does not reach it. A unit like BG1300, whose tests and mutants change HOME confinement, therefore cannot be proved in the worktree lane the sprint dispatches, and nothing in the brief or the planner says so.

## Steps to Reproduce

Brief BG1300 and spawn its builder with worktree isolation: every HOME= command is refused.

## Proposed Fix

Let a unit declare HOME isolation and have lane brief and the planner route it to a main-checkout lane.

## Acceptance Criteria

- [ ] **AC1** Given a unit that declares it needs a temporary HOME, when its lane brief is printed, then the brief names the non-worktree path (a main-checkout lane run last, with other commits held) instead of the worktree lane. Fails on: a worktree lane briefed for it.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_brief_handover.py::BriefHandoverTests::test_a_home_isolated_unit_is_briefed_for_the_main_checkout
  - **Verified:** yes (2026-11-13)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-12 | Claude Opus 5.5 (run ten orchestrator) | Filed |
