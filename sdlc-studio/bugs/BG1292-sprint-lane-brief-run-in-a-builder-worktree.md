# BG1292: `sprint lane brief` run in a builder worktree that is behind the root's branch prints the worktree's stale copy of the unit without a warning

> **Status:** Open
> **Severity:** Low
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_lane_builder_brief.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py
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

- [ ] **AC1** The behaviour described is corrected: A builder spawned with the harness's worktree isolation gets a worktree cut from the remote's default branch, not the local HEAD.
- [ ] **AC2** Following the recorded steps no longer reproduces the defect: Commit a change to a unit's criteria on local main without pushing.
- [ ] **AC3** The proposed fix lands, pinned by a test: When `lane brief` runs in a linked worktree whose HEAD is not a descendant of the main worktree's branch tip, print a WARNING naming both commits and the `git...

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-08 | Claude Opus 5.5 | Filed |
