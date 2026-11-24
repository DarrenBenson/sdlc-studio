# BG1514: Two serial-phase tests go red in the release boundary's module-alone lane under load and pass alone on the same host, so a tag push can be refused by a flake

> **Status:** Fixed
> **Severity:** Medium
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/tests/test_lean_test_selection.py, .claude/skills/sdlc-studio/scripts/tests/test_verify_lane_batch.py, tools/remote-gate.sh, tools/tests/test_remote_gate_release.py, changelog.d/BG1514.md
> **Created:** 2026-11-16
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-16T18:15:24Z

## Summary

The v6.4.0 tag push's release boundary (gate on devserver1, f5317b26) failed only the module-alone lane, on two of its fourteen serial-phase modules: `test_lean_test_selection` `SchedulingTests.test_a_sibling_temp_file_cannot_redden_the_leak_check` (5 != 0, 'the sibling never wrote, so a pass proves nothing') and `test_verify_lane_batch` `ProjectConfigurationTests.test_a_serial_only_mark_from_a_hook_runs_in_the_serial_phase` (its message begins 'the parallel phase exited 1 with no usable', the rest clipped by the gate). Run alone on the same host with the gate's Python 3.14.4, each passed twice; locally they pass too. The same commit had passed gate.py --release and the push boundary. The refusal also named a full log at /home/ops/sdlc-gate/local/<clone>/boundary-suite-last.log that did not exist when read minutes later.

## Steps to Reproduce

1. Push a release tag so pre-push runs gate.py --boundary release on the gate host.
2. The module-alone lane runs 428 modules on 8 workers, then the serial phase; under that load the two tests above can read red.
3. Run either module alone on the same host: it passes.

## Proposed Fix

Make each test wait on the event it asserts (the sibling's write, the parallel phase's output) with a bounded deadline rather than a fixed window, or move them where the lane's load cannot starve them; and keep the boundary log the refusal names until the next run.

## Acceptance Criteria

- [ ] **AC1** Given a sibling process that starts late, as it does when the module-alone lane loads every worker, when the leak check's test runs, then it waits on the sibling's write up to a bounded deadline before judging, and passes. Fails on: a fixed window the sibling outlasts, read as 'the sibling never wrote'.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_test_selection.py::SchedulingTests::test_the_leak_check_waits_for_a_sibling_that_writes_late
  - **Verified:** yes (2026-11-24)
- [ ] **AC2** Given a parallel phase slowed the same way, when the serial-only mark's test runs, then it waits on the phase's output up to a bounded deadline, and a phase that never produces one fails with its whole message rather than a clipped one. Fails on: the test reading red under load and green alone on the same host.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_verify_lane_batch.py::ProjectConfigurationTests::test_a_serial_only_mark_is_judged_once_a_slow_parallel_phase_has_reported
  - **Verified:** yes (2026-11-24)
- [ ] **AC3** Given a boundary run the gate host refuses, when the refusal names its full log, then that log exists at the named path and is still there until the next boundary run for the clone replaces it. Fails on: a refusal naming a log that is gone minutes later, so a flake cannot be told from a fault.
  - **Verify:** pytest tools/tests/test_remote_gate_release.py::RemoteReleaseGateTests::test_the_log_a_refusal_names_is_kept_until_the_next_run
  - **Verified:** yes (2026-11-24)

## Impact

A release tag push costs a second 25-minute boundary run on a flake, and the refusal's named log cannot be read to tell a flake from a fault.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-16 | sdlc-studio | Filed |
