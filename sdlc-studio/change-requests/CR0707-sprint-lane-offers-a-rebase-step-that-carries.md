# CR-0707: sprint lane offers a rebase step that carries a waiting lane's staged work onto a moved main

> **Status:** In Progress
> **Decomposed-into:** EP0347
> **Priority:** Medium
> **Type:** Enhancement
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/lib/lanes.py, .claude/skills/sdlc-studio/help/sprint.md, .claude/skills/sdlc-studio/reference-sprint-toolchain.md, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py
> **Evidence:** Run thirteen (RUN-01M7EYR3): rebases of the memory, toclass, close and US1064-repair worktrees; the slip and SHA recovery during the memory-lane rebase.
> **Date:** 2026-11-15
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-15T18:01:31Z

## Summary

When a lane finishes building while main moves under it (another lane lands first), the orchestrator rebases the worktree's staged, uncommitted work by hand: stash push, fast-forward to main, stash apply without --index, resolve each conflict, regenerate the docgen surface page, the command audit and the root-census totals, re-stage, then drop the stash. Run thirteen did this five times. Once, a chained `git stash apply --index` failed on conflicts and the following `git stash drop` still ran; the work was recovered only from the stash commit by its SHA. No command performs the step, so each orchestrator hand-rolls it and can lose a lane's work.

## Impact

A lane's staged work can be lost to a hand-rolled rebase, and each rebase costs the orchestrator's context and minutes that a command would not.

## Acceptance Criteria

_None yet: add them here, or on the stories `refine` decomposes this into._

## Proposed Fix

Add `sprint.py lane rebase --worktree <path>`: stash the staged work under a tag, fast-forward the worktree to main, apply the stash without --index, stop on a conflict leaving the stash in place and naming the files, and on a clean apply regenerate the derived pages (surface, command audit, census totals) and re-stage, dropping the stash only after the apply and re-stage succeed.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-15 | sdlc-studio | Raised |
