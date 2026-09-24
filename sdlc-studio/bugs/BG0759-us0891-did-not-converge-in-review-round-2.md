# BG0759: US0891 did not converge in review: round 2 REJECT findings

> **Status:** Open
> **Severity:** Medium
> **Points:** 3
> **Affects:** .githooks/pre-commit, tools/tests/test_lean_precommit_parallel.py, tools/tests/test_precommit_lane_order.py, tools/tests/test_message_first_gate.py, tools/tests/test_precommit_window_guard.py
> **Created:** 2026-09-24
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

US0891 was rejected at round 2, the review cap, by qa-rev-US0891, so it was carried as a known issue rather than reviewed again. The findings still open: [new] a terminal hangup or dropped SSH now orphans every lane, because set -m moves each lane out of the caller's process group and there is no HUP trap - verified fix is one line, trap 'stop\_lanes 129' HUP, and the round-2 patch is kept at sdlc-studio/.local/US0891-carried-r2.patch; [new] non-blocking: the kill\_lane test stub can SIGKILL the test runner's group leader when set -m is absent, so guard it; [new] non-blocking: dropping the TERM trap or stop\_lanes' wait survives the suite [LC-002]; [new] non-blocking: stop\_lanes signals already-reaped lane pids after collect, clear lane\_pids; [new] non-blocking: Affects still omits test\_precommit\_gate\_cost\_claim.py

## Steps to Reproduce

1. Read the round 2 REJECT of US0891 in the verdict ledger.

## Proposed Fix

Fix each finding above, then deliver US0891 again in a later run.

## Acceptance Criteria

- [ ] **AC1** The behaviour described is corrected: US0891 was rejected at round 2, the review cap, by qa-rev-US0891, so it was carried as a known issue rather than reviewed again.
- [ ] **AC2** The proposed fix lands, pinned by a test: Fix each finding above, then deliver US0891 again in a later run.

## Where the work is

The round-2 implementation is complete except for one line and is kept, uncommitted, in the
worktree of branch `worktree-agent-a664bc3f1099120b0`, with a copy at
`sdlc-studio/.local/US0891-carried-r2.patch` on the machine that ran RUN-01M39MC0. The verified
remaining fix is `trap 'stop_lanes 129' HUP` beside the INT and TERM traps (0 surviving lanes
after a pty hangup). Measured with the change: pre-commit 49s to 17s on a quiet machine.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-24 | sdlc-studio | Filed |
