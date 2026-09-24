# BG0746: The spec-claims timing claim deadlocks every fresh worktree under parallel load

> **Status:** Fixed
> **Severity:** Medium
> **Points:** 2
> **Affects:** tools/check_spec_claims.py, sdlc-studio/tsd.md, tools/tests/test_check_spec_claims.py, tools/tests/test_lean_commit_lanes.py
> **Verification depth:** functional (the criteria drive the real pre-commit and commit-msg hooks in throwaway repositories and assert the spec-claims lane, its timing claim and its checker are gone, and that a slow first timing sample never blocks a commit)
> **Created:** 2026-09-23
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

The pre-commit spec-claims lane judges tsd.md's skill-tests <= 950s claim against the median of the clone's own machine-local timing store, and it refuses before any suite runs. A fresh worktree's first sample, taken while other lanes run suites, exceeds 950s, becomes the median, and then blocks every commit, so no new sample can ever clear it. Every lane of RUN-01M36R3D hit it. The back-to-basics review lists the lane for deletion.

## Steps to Reproduce

In a fresh worktree, make one commit while other suites run so the first skill-tests sample exceeds 950s, then commit again: spec-claims refuses before any suite runs, forever.

## Proposed Fix

Delete the timing claim lane (it checks docs against docs), or judge timing claims only at the push boundary against the main clone's record.

## Acceptance Criteria

- [x] **AC1** The behaviour described is corrected: The pre-commit spec-claims lane judges tsd.md's skill-tests <= 950s claim against the median of the clone's own machine-local timing store, and it refuses...
- [x] **AC2** Following the recorded steps no longer reproduces the defect: In a fresh worktree, make one commit while other suites run so the first skill-tests sample exceeds 950s, then commit again: spec-claims refuses before any...
- [x] **AC3** The proposed fix lands, pinned by a test: Delete the timing claim lane (it checks docs against docs), or judge timing claims only at the push boundary against the main clone's record.
  - **Verify:** pytest tools/tests/test_lean_commit_lanes.py::CommitLaneTests
  - **Verified:** yes (2026-09-24)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-23 | sdlc-studio | Filed |
| 2026-09-24 | Claude Opus 5.5 | Fixed by US0879 (RUN-01M3891F): the story's criteria are this bug's proposed fix, and its test class verifies it here |
