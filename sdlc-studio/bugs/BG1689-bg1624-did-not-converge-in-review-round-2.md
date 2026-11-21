# BG1689: BG1624 did not converge in review: round 2 REJECT findings

> **Status:** Open
> **Severity:** Medium
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/tests/test_lane_run.py, .claude/skills/sdlc-studio/scripts/lib/lanes.py, changelog.d/BG1624.md, .claude/skills/sdlc-studio/scripts/tests/test_lane_timeout_index_lock.py
> **Created:** 2026-11-21
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-21T18:05:06Z

## Summary

BG1624 was rejected at round 2, the review cap, by Sam Eriksson (qa), so it was carried as a known issue rather than reviewed again. The findings still open: BLOCKING: [new] on the path where the lane's CLI exits on its own (lanes.py:1467-1468, `if _kill_group(proc): _clear_killed_lock(lock, before)`), neither guard that keeps a lock the killed group did not take is pinned. The sentence this repair adds to changelog.d/BG1624.md says the removal, and the leaving of a lock "there before it started", hold "at a timeout and when the lane's CLI exits on its own ... and a case pins each". The one exit case, `test_a_lane_that_exits_on_its_own_has_its_killed_child_s_lock_removed`, pins only the removal. Two mutants each survived `test_lane_timeout_index_lock.py` and `test_lane_run.py` (24 passed, 18 subtests): passing `None` for `before` on that path, and clearing whether or not SIGKILL was sent. Both are live in isolation through `sprint.main`, with this module's fake `codex` given two more exit modes. With a lock in the worktree before the run, and a CLI that exits leaving a SIGTERM-deaf child that takes no lock, HEAD leaves the lock untouched, and the first mutant deletes it and prints "removed". With a CLI that takes the lock itself and exits, so the group empties on the SIGTERM and no SIGKILL is sent, HEAD leaves the lock, and the second mutant deletes it. That is the deletion of another process's lock that the timeout cases guard against, unguarded on the exit path; RULINGS: Round-1 "no test pins the lock clearing on the path where the lane's CLI exits on its own" is CLOSED for the clearing itself. The new exit case kills the bare `_kill_group(proc)` mutant (author replay killed) and passes at HEAD. The guards on that same path are the new finding above. AC1 is met: `verify_ac.py run --id BG1624 --dry-run` passes AC1, and the module passed 5 of 5 (4 subtests) at HEAD. Claim inventory: the new `exit` mode comment and the case's docstring are TRUE by execution. The changelog's added clause "a case pins each" is FALSE, as above.

## Steps to Reproduce

1. Read the round 2 REJECT of BG1624 in the verdict ledger.

## Proposed Fix

Fix each finding above, then deliver BG1624 again in a later run.

## Acceptance Criteria

- [ ] **AC1** The round 2 REJECT finding no longer holds: BLOCKING: [new] on the path where the lane's CLI exits on its own (lanes.py:1467-1468, `if _kill_group(proc): _clear_killed_lock(lock, before)`), neither guard that keeps a lock the killed group did not take is pinned. The sentence this repair adds to changelog.d/BG1624.md says the removal, and the leaving of a lock "there before it started", hold "at a timeout and when the lane's CLI exits on its own ... and a case pins each". The one exit case, `test_a_lane_that_exits_on_its_own_has_its_killed_child_s_lock_removed`, pins only the removal. Two mutants each survived `test_lane_timeout_index_lock.py` and `test_lane_run.py` (24 passed, 18 subtests): passing `None` for `before` on that path, and clearing whether or not SIGKILL was sent. Both are live in isolation through `sprint.main`, with this module's fake `codex` given two more exit modes. With a lock in the worktree before the run, and a CLI that exits leaving a SIGTERM-deaf child that takes no lock, HEAD leaves the lock untouched, and the first mutant deletes it and prints "removed". With a CLI that takes the lock itself and exits, so the group empties on the SIGTERM and no SIGKILL is sent, HEAD leaves the lock, and the second mutant deletes it. That is the deletion of another process's lock that the timeout cases guard against, unguarded on the exit path
  - **Verify:** manual - the independent review of the redelivery re-checks this finding
- [ ] **AC2** BG1624 AC1 still passes: Given a lane run with `--timeout 1` whose git add loop is killed under a loaded host's parallel suite, when `sprint.py lane run` stops it, then no `index.lock` is left in the worktree on any of repeated runs, and a SIGKILL-first kill order still fails the test. Fails on: a killed git add leaves index.lock, so the test fails intermittently on the gate host.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lane_timeout_index_lock.py::TimedOutGitAddLeavesNoLockTests

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-21 | sdlc-studio | Filed |
