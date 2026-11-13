# BG1390: test_lean_tracked_run_record test_this_repos_signed_reports_check_in_a_clean_clone fails in a harness worktree

> **Status:** Open
> **Severity:** Low
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/scripts/tests/test_lean_tracked_run_record.py, .claude/skills/sdlc-studio/scripts/tests/test_signed_reports_clean_clone_in_worktree.py, changelog.d/BG1390.md
> **Evidence:** RUN-01M78TKD, 2026-11-13: lane cost builder
> **Created:** 2026-11-13
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5 (run eleven orchestrator); agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-13T01:08:58Z

## Summary

The test git-clones the worktree path, which exits 128 inside a harness worktree.

## Steps to Reproduce

Run the test from a lane worktree.

## Proposed Fix

Clone from `git rev-parse --git-common-dir` or skip.

## Acceptance Criteria

- [ ] **AC1** Given a harness worktree, when the clean-clone test runs, then it clones the repository's common git dir or skips with a stated reason. Fails on: git clone exiting 128.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_signed_reports_clean_clone_in_worktree.py::SignedReportsCleanCloneInWorktreeTests

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-13 | Claude Opus 5.5 (run eleven orchestrator) | Filed |
