# BG0837: The pre-push gate judges the working tree, not the commits being pushed, so an uncommitted fix turns a red push green

> **Status:** Open
> **Groomed:** 2026-10-01 (D0291) - premise reproduced at HEAD: `.githooks/pre-push` (190 lines) runs `python3 "$skill/gate.py" --boundary push` in the working tree and holds no `stash`, `worktree` or dirty-tree check (grep finds none), so the gate imports uncommitted files. Narrowed to the accuracy fix: the `refuse a dirty push` option is dropped as a new refusal (D0291)
> **Severity:** Medium
> **Points:** 3
> **Affects:** .githooks/pre-push, tools/tests/test_lean_prepush_pushed_commit.py, tools/tests/test_pre_push_hook.py, changelog.d/BG0837.md
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

Run the boundary gate in a temporary `git worktree` checked out at the pushed tip (`node_modules` symlinked from the clone), removed on exit. A dirty tree is neither refused nor touched: the pusher's uncommitted work stays where it is, and the gate judges exactly what CI will check out.

## Acceptance Criteria

- [ ] **AC1** Given a fixture clone whose committed stub `gate.py` exits 1 and whose working-tree copy is edited to exit 0, uncommitted, when `git push` runs the tracked pre-push hook, then the push is refused, and the working-tree edit is still present afterwards. Fails on: HEAD, which runs the working-tree stub and lets the push through
  - **Verify:** pytest tools/tests/test_lean_prepush_pushed_commit.py::PrePushPushedCommitTests::test_the_gate_judges_the_pushed_commit
- [ ] **AC2** Given the same clone with the stub committed green and a red edit left uncommitted, when `git push` runs the hook, then the push goes through. Fails on: HEAD, which refuses on the uncommitted red edit; and on a fix that refuses any dirty tree
  - **Verify:** pytest tools/tests/test_lean_prepush_pushed_commit.py::PrePushPushedCommitTests::test_an_uncommitted_red_edit_does_not_refuse_a_green_commit

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-28 | sdlc-studio | Filed |
