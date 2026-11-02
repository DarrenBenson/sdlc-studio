# BG1147: The pre-commit markdown lane skips in a linked worktree, because it looks for markdownlint only in that worktree's node_modules

> **Status:** Open
> **Severity:** Medium
> **Points:** 2
> **Affects:** .githooks/pre-commit, tools/tests/test_lean_commit_lanes.py, changelog.d/BG1147.md
> **Evidence:** 2026-11-01: builder reports for US1098, BG0963, BG1139, BG1140 and US1105 each say 'markdown skipped: markdownlint is not installed'; node_modules/.bin/markdownlint exists in the main tree.
> **Created:** 2026-11-01
> **Created-by:** sdlc-studio file
> **Raised-by:** claude; human; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-01T02:09:32Z

## Summary

.githooks/pre-commit:293 runs `node_modules/.bin/markdownlint` relative to the worktree root, then falls back to a markdownlint on PATH. A linked worktree (`git worktree add`) has no `node_modules`, so every commit made in one prints 'SKIP markdown - markdownlint not found' and lands unlinted markdown. Every builder in RUN-01M6A3K2 committed from a worktree; US1105's commit put four markdownlint errors on main, and they surfaced only when a later commit in the main tree ran the lane.

## Steps to Reproduce

1. `git worktree add ../wt main`, then stage a markdown file with an MD032 error there.
2. Commit: the markdown lane prints SKIP and the commit lands.
3. The same staged file in the main tree is refused.

## Proposed Fix

Also look for markdownlint in the main worktree's `node_modules` (resolve `git rev-parse --git-common-dir`, then its parent), and name the path used. A worktree commit then runs the same lane as a main-tree commit.

## Acceptance Criteria

- [ ] **AC1** A commit made in a linked worktree runs the markdown lane with the main worktree's markdownlint when its own `node_modules` is absent, and refuses a markdown error as the main tree does.
  - **Verify:** pytest tools/tests/test_lean_commit_lanes.py::CommitLaneTests::test_markdown_lane_in_a_linked_worktree_uses_the_main_worktrees_markdownlint
- [ ] **AC2** With no markdownlint anywhere, the lane still prints SKIP naming what it looked for (the positive control).
  - **Verify:** pytest tools/tests/test_lean_commit_lanes.py::CommitLaneTests::test_markdown_skip_names_every_place_it_looked

## Impact

A gate the main tree enforces is silently off for every delegated builder, which is the commit path this repository now uses for nearly all delivery.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-01 | claude | Filed |
| 2026-11-02 | Claude Opus 5.5 (grooming) | Re-groomed under D0399: each criterion's Verify names its own node (the whole module was green before the fix). Mutants: AC1, look only in ./node_modules (pre-commit:293); AC2, print SKIP without the paths |
