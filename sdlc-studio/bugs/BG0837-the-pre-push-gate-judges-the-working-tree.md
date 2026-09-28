# BG0837: The pre-push gate judges the working tree, not the commits being pushed, so an uncommitted fix turns a red push green

> **Status:** Open
> **Severity:** Medium
> **Points:** 3
> **Affects:** .githooks/pre-push, tools/tests/test_lean_prepush_pushed_commit.py, changelog.d/BG0837.md
> **Evidence:** followups line 25; CI run 36336415797; HEAD 7e53a438 .githooks/pre-push (no stash, worktree or dirty check)
> **Created:** 2026-09-28
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-09-28T16:27:10Z

## Summary

At 0aa334cb the pre-push gate passed because BG0785's status fix sat uncommitted in the working tree; CI, checking out the commit, went red on US0063 AC1 (run 36336415797). `.githooks/pre-push` runs `gate.py --boundary push` against the working tree and has no dirty-tree handling.

## Steps to Reproduce

Leave a fix uncommitted, push the commit without it: the hook passes; CI fails.

## Proposed Fix

Run the boundary gate in a temporary worktree at the pushed tip, or refuse a push from a dirty tree naming the files.

## Acceptance Criteria

- [ ] **AC1** Given a working tree with an uncommitted change to a tracked file under test, when the pre-push hook runs, then it gates the pushed commit (or refuses naming the dirty files). Fails on: HEAD, which gates the working tree
  - **Verify:** pytest tools/tests/test_lean_prepush_pushed_commit.py::PrePushPushedCommitTests::test_the_gate_judges_the_pushed_commit

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-28 | sdlc-studio | Filed |
