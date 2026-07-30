# BG0445: the test-census lane skips any path containing `worktrees`, so it censuses zero files and reports an all-clear precisely where this repo runs its reviewers

> **Status:** Open
> **Severity:** Medium
> **Points:** 2
> **Affects:** tools/test_census.py, tools/tests/test_test_census.py
> **Created:** 2026-07-30
> **Created-by:** sdlc-studio file
> **Raised-by:** engineering amigo seat (independent, isolated worktree); human; v1
> **Raised-in-batch:** 2026-07-29T15:35:33Z

## Summary

`tools/test_census.py` matches its skip list against the ABSOLUTE path parts, and the list contains `worktrees`. Any repository root beneath `.claude/worktrees/` therefore has every file skipped: the census counts zero, and the lane reports an all-clear over nothing. This repo runs its adversarial reviewers and its parallel delivery agents in worktrees, so the lane is inert in exactly the environment it is relied on.

## Steps to Reproduce

Observed at d7a1ad8f, 2026-07-30, by the engineering amigo seat running the tools suite from inside its own isolated worktree:

```text
python3 -m unittest discover -s tools/tests
FAIL: `test_test_census.RealRepoTests.test_this_repos_test_files_are_mostly_attributed`
AssertionError: 0 not greater than 100
```

The failure is the honest signal - the assertion caught the empty census. The defect is that in any lane not making that assertion, the same emptiness reads as a pass.

Last touched by b086e869, a prior sprint, so this is NOT a regression from the batch under review; it is reported because the reviewer hit it and because a guard that is inert in worktrees is worth knowing about while worktrees are the review mechanism.

## Proposed Fix

Match the skip list against the path RELATIVE to the census root, not the absolute path. A directory name appearing somewhere above the root says nothing about the files below it. Pin it with a test that runs the census from a root nested under a directory named `worktrees` and asserts a non-zero count - the existing assertion catches the symptom in this repo but nothing prevents the same shape recurring for `node_modules`, `.venv` or any other name in the list.

## Acceptance Criteria

- [ ] The behaviour described is corrected: `tools/test_census.py` matches its skip list against the ABSOLUTE path parts, and the list contains `worktrees`.
- [ ] Following the recorded steps no longer reproduces the defect: Observed at d7a1ad8f, 2026-07-30, by the engineering amigo seat running the tools suite from inside its own isolated worktree: The failure is the honest signal...
- [ ] The proposed fix lands, pinned by a test: Match the skip list against the path RELATIVE to the census root, not the absolute path.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-30 | engineering amigo seat (independent, isolated worktree) | Filed |
