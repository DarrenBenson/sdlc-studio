# BG1470: lane land runs the full commit hooks, then refuses the rebase over an unstaged author-self-checks.md the builder's self-check left in the worktree

> **Status:** Open
> **Severity:** Medium
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/lib/lanes.py, .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_lane_land.py, changelog.d/BG1470.md, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py
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

- [ ] **AC1** The behaviour described is corrected: A builder runs `critic.py self-check record` in its worktree, as the brief asks, which appends rows to sdlc-studio/reviews/author-self-checks.md, and it leaves...
- [ ] **AC2** The proposed fix lands, pinned by a test: Before the commit, have lane land check for unstaged or untracked changes in the worktree.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-15 | sdlc-studio | Filed |
