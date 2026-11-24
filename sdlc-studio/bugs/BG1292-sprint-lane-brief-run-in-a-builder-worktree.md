# BG1292: `sprint lane brief` run in a builder worktree that is behind the root's branch prints the worktree's stale copy of the unit without a warning

> **Status:** Open
> **Supersedes:** BG1338
> **Severity:** Low
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_lane_builder_brief.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py, changelog.d/BG1292.md
> **Evidence:** the 6.3.0 release builders, 2026-11-08 (BG1248's BLOCKED hand-back)
> **Created:** 2026-11-08
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-08T13:55:29Z

## Summary

A builder spawned with the harness's worktree isolation gets a worktree cut from the remote's default branch, not the local HEAD. Grooming committed locally but not yet pushed is therefore absent from the builder's copy: on 2026-11-08 the BG1248 and BG1249 builders briefed the pre-grooming bug (no Verify lines, old Affects), and BG1248 returned BLOCKED on it. `lane brief` reads the unit from the worktree and says nothing about the worktree's branch being behind the root's.

## Steps to Reproduce

Commit a change to a unit's criteria on local main without pushing. Create a worktree from origin/main and run `sprint.py lane brief --units <unit>` in it: the old criteria print, with no warning.

## Proposed Fix

When `lane brief` runs in a linked worktree whose HEAD is not a descendant of the main worktree's branch tip, print a WARNING naming both commits and the `git merge --ff-only <branch>` that brings the unit up to date; say in the sprint reference that a builder fast-forwards first.

## Acceptance Criteria

- [ ] **AC1** Given a linked worktree whose HEAD is not a descendant of the main worktree's branch tip, where that tip holds a newer commit to the unit's criteria, when `sprint.py lane brief --units <unit>` runs in the worktree, then stderr carries a WARNING naming both commits and the `git merge --ff-only <branch>` that brings the unit up to date. Fails on: the worktree's stale copy of the unit briefed with no warning.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lane_builder_brief.py::BuilderBriefTests::test_a_worktree_behind_the_roots_branch_is_warned_with_the_fast_forward
- [ ] **AC2** Given a linked worktree at or ahead of the main worktree's branch tip, and the main worktree itself, when `lane brief` runs in each, then no such warning is printed and the brief is the one printed today. Fails on: a warning on every brief, which a builder learns to ignore.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lane_builder_brief.py::BuilderBriefTests::test_an_up_to_date_worktree_and_the_root_are_not_warned
- [ ] **AC3** Given a builder briefed by `lane brief` in a harness worktree that starts at origin's commit, the brief names the fast-forward step and the base the builder must be at before building (carried from BG1338). Fails on: the brief names neither the step nor the base, so a harness worktree builds on origin's stale commit.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lane_builder_brief.py::BuilderBriefTests::test_the_brief_names_the_fast_forward_step_and_the_base_to_build_on

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-08 | Claude Opus 5.5 | Filed |
| 2026-11-24 | orchestrator (delegate under D0545) | Affects widened for run twenty-six's SPA lane: AC3 given a Verify line; it had none, so no run could judge it (the plan's unspecified-criteria advisory) |
