# BG0759: US0891 did not converge in review: round 2 REJECT findings

> **Status:** Open
> **Carried work:** the round-2 patch is kept at sdlc-studio/.local/US0891-carried-r2.patch, written against 08b60ce7. It no longer applies to `.githooks/pre-commit`: US0899 and US0901 changed the hook since. Remaining fix: rebase onto US0901's `run "gate"` and `run "suite-handover"` lanes, add `trap 'stop_lanes 129' HUP`, and pin the TERM trap and `stop_lanes`' wait
> **Severity:** Medium
> **Points:** 3
> **Affects:** .githooks/pre-commit, changelog.d/US0891.md, tools/tests/test_lean_precommit_parallel.py, tools/tests/test_precommit_lane_order.py, tools/tests/test_precommit_gate_cost_claim.py, tools/tests/test_message_first_gate.py, tools/tests/test_lean_commit_lanes.py, tools/tests/test_precommit_window_guard.py
> **Created:** 2026-09-24
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

US0891 was rejected at round 2, the review cap, by qa-rev-US0891, so it was carried as a known issue rather than reviewed again. The findings still open: [new] a terminal hangup or dropped SSH now orphans every lane, because set -m moves each lane out of the caller's process group and there is no HUP trap - verified fix is one line, trap 'stop\_lanes 129' HUP, and the round-2 patch is kept at sdlc-studio/.local/US0891-carried-r2.patch; [new] non-blocking: the kill\_lane test stub can SIGKILL the test runner's group leader when set -m is absent, so guard it; [new] non-blocking: dropping the TERM trap or stop\_lanes' wait survives the suite [LC-002]; [new] non-blocking: stop\_lanes signals already-reaped lane pids after collect, clear lane\_pids; [new] non-blocking: Affects still omits test\_precommit\_gate\_cost\_claim.py

The criteria take the blocking HUP finding, the LC-002 finding on the TERM trap and wait, and the rebase the hook now needs. Also fix, unpinned: guard the `kill_lane` stub, clear `lane_pids` after `collect`. The Affects omission is closed here.

## Steps to Reproduce

At 65cdf1ca, `git apply --check` of the carried patch fails on `.githooks/pre-commit`. A three-way merge onto HEAD conflicts in two hunks, both US0901's gate lane. Resolving them to HEAD's `run "gate"` gives a hook whose `--list` prints all 15 lanes, but:

1. `test_lean_precommit_parallel.py`: 7 tests error with `AttributeError`, because `_declared_lanes` cannot read `-- gate_lane`.
2. `test_message_first_gate.py::HandoffTests::test_a_handover_that_cannot_be_written_refuses_rather_than_passing_quietly` fails: US0901's `run "suite-handover"` now starts a background lane, and `$fail` is read before any `collect`, so an unwritable handover passes the commit.
3. The merged hook traps INT and TERM only.

HEAD itself still runs the lanes one after another (no `lane`, `collect` or `set -m`).

## Proposed Fix

Rebase the carried patch onto HEAD: keep the gate as `run "gate"`, read the lanes in `_declared_lanes` from `--list`, run or collect `suite-handover` before `$fail` is read, and add `trap 'stop_lanes 129' HUP` beside the INT and TERM traps.

## Acceptance Criteria

- [ ] **AC1** Given the rebased hook in the patch's hermetic fixture with five lanes (the gate among them) stubbed to sleep 2s, when a commit runs, then all five are running at one moment and the hook's wall time is under 60% of their summed 10s, with the lanes read from `pre-commit --list`. Fails on: HEAD's sequential lanes, and on the naive rebase whose `_declared_lanes` cannot read `run "gate" -- gate_lane`.
  - **Verify:** pytest tools/tests/test_lean_precommit_parallel.py::ParallelLaneTests::test_the_lanes_run_concurrently
- [ ] **AC2** Given the rebased hook and a git directory where the suite handover cannot be written, when a commit whose lanes all pass runs, then it is refused naming `suite-handover`, and a writable handover still passes. Fails on: the naive rebase, measured, where `run "suite-handover"` backgrounds the lane and `$fail` is read before `collect`.
  - **Verify:** pytest tools/tests/test_lean_precommit_parallel.py::ParallelLaneTests::test_an_unwritable_handover_still_refuses_with_the_lanes_parallel
- [ ] **AC3** Given every lane running, when the hook's process group receives SIGHUP (a terminal hangup or dropped SSH) and, in a second case, SIGTERM, then no lane process survives, nothing writes after the hook exits, the hook exits 129 or 143, and no lane buffer is left under TMPDIR. Fails on: the carried patch, which has no HUP trap; dropping the TERM trap; dropping `stop_lanes`' `wait`, which lets the EXIT trap remove the buffers while lanes still write.
  - **Verify:** pytest tools/tests/test_lean_precommit_parallel.py::ParallelLaneTests::test_a_hangup_or_terminate_stops_every_lane_with_the_hook

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
| 2026-09-25 | QA seat | Groomed for Sprint 4: still real (HEAD runs the lanes sequentially; the patch no longer applies, and resolving it to HEAD's gate lane breaks 7 patch tests and lets an unwritable handover pass); criteria are the rebased patch, the handover regression and the HUP/TERM fix, each with one Verify line and the wrong fix it fails on; Affects adds test_precommit_gate_cost_claim.py, test_lean_commit_lanes.py and the changelog; 3 points stand |
