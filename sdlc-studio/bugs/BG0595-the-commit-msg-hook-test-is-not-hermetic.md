# BG0595: the commit-msg hook test is not hermetic, so the full suite goes red whenever the working tree is dirty

> **Status:** Open
> **Severity:** Medium
> **Points:** 2
> **Affects:** tools/tests/test_commit_msg_hook.py
> **Created:** 2026-08-18
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** 2026-08-18T20:35:22Z

## Summary

`HonestDegradeTests::test_no_argument_does_not_block` runs the real `.githooks/commit-msg` against the REAL repository and asserts exit 0. The hook's `repo-writes` lane reports every path that differs from HEAD, so the test fails whenever the working tree carries uncommitted work - which is its state during every delivery, by construction. The failure names the author's own in-flight edits as though the test run had written them.

## Steps to Reproduce

Measured 2026-08-18 at e9f7baf7. With 15 uncommitted paths, `bash tools/run-suite.sh all` reports `FAILED (failures=1)` and the log shows `FAIL repo-writes ... the test run changed 15 path(s)`, listing the working tree's own modifications. `git stash push -u` then re-running the same test alone: 1 passed. `git stash pop` and it fails again. The test's verdict is therefore a property of the working tree rather than of the code under test.

## Proposed Fix

Run the hook against a throwaway git repository rather than the one under development, as the sibling hook tests do, or set the environment the lane reads so `repo-writes` is scoped to a fixture. The bar is that the test's result must not change when a developer has unrelated uncommitted work. Check the other tests in this file for the same coupling before assuming it is the only one - a non-hermetic test that fails only during delivery is one people learn to ignore, which is worse than not having it.

## Acceptance Criteria

- [ ] **AC1** The behaviour described is corrected: `HonestDegradeTests::test_no_argument_does_not_block` runs the real `.githooks/commit-msg` against the REAL repository and asserts exit 0.
- [ ] **AC2** The proposed fix lands, pinned by a test: Run the hook against a throwaway git repository rather than the one under development, as the sibling hook tests do, or set the environment the lane reads so...

## Impact

The full suite is the gate for push, release and close. A lane that goes red purely because work is in flight trains the operator to read a red full suite as noise, which is the state in which a real failure ships.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-18 | sdlc-studio | Filed |
