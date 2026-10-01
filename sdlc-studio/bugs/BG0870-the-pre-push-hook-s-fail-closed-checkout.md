# BG0870: The pre-push hook's fail-closed checkout and annotated-tag peel are unpinned, it runs the release lanes on a branch tip pushed beside a tag, and an interrupted push leaves a prunable worktree

> **Status:** Open
> **Severity:** Medium
> **Points:** 2
> **Affects:** .githooks/pre-push,tools/tests/test_pre_push_hook.py,tools/tests/test_lean_prepush_pushed_commit.py,changelog.d/BG0870.md
> **Evidence:** BG0837 QA review, RUN-01M3VF2J, 2026-10-01
> **Created:** 2026-10-01
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-10-01T11:21:51Z

## Summary

From BG0837's QA review (RUN-01M3VF2J, APPROVE): (1) a failed `git worktree add` refuses the push and names the bypass, but changing that `exit 1` to `exit 0` (.githooks/pre-push:194) lands commits with no gate run and every test stays green, so the hook can turn fail-open unnoticed; (2) an annotated tag runs the gate once only because the hook peels it to its commit (.githooks/pre-push:30), and the once-only test uses lightweight tags, so removing the peel doubles a release push unseen; (3) when a push carries refs at different commits, each is judged (correct) but the shared boundary runs the release-only lanes on the branch tip too, about ten minutes wasted, and the header comment says it runs once; (4) on SIGINT/SIGTERM `drop_worktree` runs with the cwd inside the removed tree, so the worktree registration is left prunable (cleared by the next push).

## Steps to Reproduce

In a fixture clone: make .git/worktrees read-only and push - refused; apply the exit 0 mutant - the push lands with zero gate calls and the hook tests pass.

## Proposed Fix

Pin the fail-closed checkout and the annotated-tag peel with tests; choose the boundary per pushed commit (release only for a commit a tag points at); `cd "$repo_root"` at the top of `drop_worktree`; correct the header comment.

## Acceptance Criteria

- [ ] **AC1** Given a fixture clone where `git worktree add` fails, when `git push` runs the hook, then the push is refused and the remote is unchanged. Fails on: an `exit 0` at the checkout-failure branch, which the current tests let through
  - **Verify:** pytest tools/tests/test_pre_push_hook.py::PrePushWorktreeTests::test_a_failed_checkout_refuses_the_push
- [ ] **AC2** Given main and an annotated tag on the same commit, when both are pushed, then the gate runs once at the release boundary. Fails on: a hook that does not peel the tag
  - **Verify:** pytest tools/tests/test_pre_push_hook.py::PrePushWorktreeTests::test_an_annotated_tag_runs_the_gate_once
- [ ] **AC3** Given main and a tag on an older commit pushed together, when the hook runs, then the branch tip is judged at the push boundary and the tagged commit at the release boundary. Fails on: the current shared boundary, which runs release lanes on both
  - **Verify:** pytest tools/tests/test_pre_push_hook.py::PrePushWorktreeTests::test_each_commit_gets_its_own_boundary

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-01 | sdlc-studio | Filed |
