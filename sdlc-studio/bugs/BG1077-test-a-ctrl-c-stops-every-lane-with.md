# BG1077: test_a_ctrl_c_stops_every_lane_with_the_hook can see every lane finish before its interrupt lands on a loaded host, and reads the hook's clean exit as a failure

> **Status:** Won't Fix
> **Severity:** Low
> **Points:** 1
> **Affects:** tools/tests/test_lean_precommit_parallel.py, changelog.d/BG1077.md
> **Evidence:** devserver1 boundary-suite log for f31862d8, 2026-10-19: `tools/tests/test_lean_precommit_parallel.py:461: AssertionError: 0 != 130`; the same test passed on the host runs of 83b76134 and earlier, and on a workstation at -n 8.
> **Created:** 2026-10-19
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-10-19T13:41:27Z

## Summary

`_signal_mid_run` (tools/tests/`test_lean_precommit_parallel.py)` gives every lane a three-second sleep, polls until it has seen every lane start, then sends SIGINT to the hook's group and expects exit 130. On devserver1, running the full suite eight-way beside a CI job, the lanes all finished before the signal was sent, the hook exited 0, and the test failed with `0 != 130`. It passed on every earlier host run and passes eight-way on a workstation, so it is a timing assumption the load breaks, not a defect in the hook.

## Steps to Reproduce

Run the push boundary's full suite on a host under heavy load (the 2026-10-19 devserver1 run of f31862d8) -> `test_a_ctrl_c_stops_every_lane_with_the_hook: AssertionError: 0 != 130`.

## Proposed Fix

Hold each lane until the test releases it (a marker file the stub lane waits on), rather than sleeping a fixed three seconds, so the signal always lands while every lane is running.

## Acceptance Criteria

- [ ] **AC1** The Ctrl-C lane test's signal always lands while every lane is still running, whatever the host's load
  - **Verify:** pytest tools/tests/test_lean_precommit_parallel.py -k ctrl_c_stops_every_lane_with_the_hook

## Impact

A push can be refused by a timing flake unrelated to the change being pushed.

## Resolution (2026-10-19): misdiagnosed - not a flake

The test failed again on the next host run with the host's load at 0.10, so load was not the cause. The cause was US1076's own change: the gate host launched its gate as a background job (`setsid python3 gate.py ... &`), and a non-interactive shell starts a background job with SIGINT and SIGQUIT ignored, which every process the gate starts inherits. The hook this test interrupts therefore could not be interrupted, and exited 0. The test was right. US1076's round-2 repair execs the gate with both signals at their defaults, and pins it with `test_the_hosts_gate_keeps_interrupts_at_their_default`. Nothing in this test needs fixing.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-19 | Claude Opus 5.5 | Filed |
| 2026-10-19 | Claude Opus 5.5 | Won't Fix: misdiagnosed. The test caught US1076's background launch ignoring SIGINT, fixed in US1076's repair |
