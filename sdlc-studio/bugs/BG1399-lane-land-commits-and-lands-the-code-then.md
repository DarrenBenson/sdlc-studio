# BG1399: lane land commits and lands the code, then refuses a self-check missing a required surface, when the builder can no longer be resumed

> **Status:** Open
> **Severity:** Medium
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/lib/lanes.py, .claude/skills/sdlc-studio/scripts/tests/test_lane_land.py, .claude/skills/sdlc-studio/scripts/tests/test_self_check_before_commit.py, changelog.d/BG1399.md
> **Evidence:** RUN-01M78TKD, 2026-11-13: orchestrator
> **Created:** 2026-11-13
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5 (run eleven orchestrator); agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-13T01:11:29Z

## Summary

The commit-message claims check runs after the commit, so the refusal arrives once the worktree and builder have gone.

## Steps to Reproduce

Land a unit whose self-check omits commit-message claims.

## Proposed Fix

Run the self-check gate before the commit.

## Acceptance Criteria

- [ ] **AC1** Given a self-check missing a required surface, when `sprint lane land` runs, then it refuses before committing and leaves the worktree intact. Fails on: the commit made first.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_self_check_before_commit.py::SelfCheckBeforeCommitTests

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-13 | Claude Opus 5.5 (run eleven orchestrator) | Filed |
