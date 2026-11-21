# BG1470: lane land runs the full commit hooks, then refuses the rebase over an unstaged author-self-checks.md the builder's self-check left in the worktree

> **Status:** Open
> **Severity:** Medium
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/lib/lanes.py, .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_lane_land.py, changelog.d/BG1470.md, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint_drive.py
> **Evidence:** Run thirteen, the US1067/US1068 repair land, 2026-11-15 (scratch land-closefix.txt): committed d59d4519, then the rebase was refused.
> **Created:** 2026-11-15
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-15T18:41:16Z

## Summary

A builder runs `critic.py self-check record` in its worktree, as the brief asks, which appends rows to sdlc-studio/reviews/author-self-checks.md, and it leaves the file unstaged because it is not in the unit's Affects. `sprint.py lane land` then commits the staged work through the hooks (about 15 minutes) and only afterwards tries to rebase the lane onto main, which git refuses with 'cannot rebase: You have unstaged changes'. The land reports 'Conflicting files: none reported by git' and asks the operator to resolve it in the worktree and land again, which runs the hooks a second time. The land records the self-check on main itself, so the worktree's rows are redundant.

## Steps to Reproduce

1. In a lane worktree, record a self-check with critic.py self-check record and stage only the unit's Affects.
2. Run sprint.py lane land --worktree <path> --units <id>.
3. See the commit pass the hooks and then the rebase fail on unstaged changes.

## Proposed Fix

Before the commit, have lane land check for unstaged or untracked changes in the worktree. Restore author-self-checks.md itself, since the land re-records the self-check on main, and refuse any other leftover file before running the hooks, naming it.

## Acceptance Criteria

- [ ] **AC1** Given a lane worktree whose builder recorded a self-check, leaving sdlc-studio/reviews/author-self-checks.md modified and unstaged beside a staged change, when `sprint.py lane land` runs, then it restores that file before the commit, the lane commits, rebases and fast-forwards in one pass, and the self-check is recorded on the root. Fails on: the rebase refused over unstaged changes after the hooks have already run.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lane_land.py::LaneLandTests::test_a_self_check_ledger_left_unstaged_does_not_stop_the_land
- [ ] **AC2** Given a worktree holding any other unstaged or untracked file outside the hand-in path, when `sprint.py lane land` runs, then it refuses before the commit, naming the file, and no commit is made and no hook runs. Fails on: the hooks running first and the refusal coming only at the rebase, or the leftover file silently discarded.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lane_land.py::LaneLandTests::test_a_leftover_file_is_refused_before_the_hooks_run
- [ ] **AC3** Given a worktree holding only its staged change, the hand-in files and the unstaged verify edit to the unit's own artefact, when `sprint.py lane land` runs, then it lands as before. Fails on: the new check refusing a clean lane, the hand-in, or the edit the land already discards.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lane_land.py::LaneLandTests::test_a_clean_lane_still_lands

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-15 | sdlc-studio | Filed |
| 2026-11-21 | Claude Opus 5.5 (run twenty-one orchestrator) | Affects widened in-run: its preflight now refuses the stopped-after-commit fixture's blocking file up front, so that test creates the file after the preflight |
