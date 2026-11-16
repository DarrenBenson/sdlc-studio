# BG1514: Two serial-phase tests go red in the release boundary's module-alone lane under load and pass alone on the same host, so a tag push can be refused by a flake

> **Status:** Open
> **Severity:** Medium
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/tests/test_lean_test_selection.py, .claude/skills/sdlc-studio/scripts/tests/test_verify_lane_batch.py
> **Created:** 2026-11-16
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-16T18:15:24Z

## Summary

The v6.4.0 tag push's release boundary (gate on devserver1, f5317b26) failed only the module-alone lane, on two of its fourteen serial-phase modules: `test_lean_test_selection` `SchedulingTests.test_a_sibling_temp_file_cannot_redden_the_leak_check` ('5 != 0 : the sibling never wrote, so a pass proves nothing') and `test_verify_lane_batch` `ProjectConfigurationTests.test_a_serial_only_mark_from_a_hook_runs_in_the_serial_phase` ('the parallel phase exited 1 with no usable ...'). Run alone on the same host with the gate's Python 3.14.4, each passed twice; locally they pass too. The same commit had passed gate.py --release and the push boundary. The refusal also named a full log at /home/ops/sdlc-gate/local/<clone>/boundary-suite-last.log that did not exist when read minutes later.

## Steps to Reproduce

1. Push a release tag so pre-push runs gate.py --boundary release on the gate host.
2. The module-alone lane runs 428 modules on 8 workers, then the serial phase; under that load the two tests above can read red.
3. Run either module alone on the same host: it passes.

## Proposed Fix

Make each test wait on the event it asserts (the sibling's write, the parallel phase's output) with a bounded deadline rather than a fixed window, or move them where the lane's load cannot starve them; and keep the boundary log the refusal names until the next run.

## Acceptance Criteria

- [ ] **AC1** The behaviour described is corrected: The v6.4.0 tag push's release boundary (gate on devserver1, f5317b26) failed only the module-alone lane, on two of its fourteen serial-phase modules...
- [ ] **AC2** The proposed fix lands, pinned by a test: Make each test wait on the event it asserts (the sibling's write, the parallel phase's output) with a bounded deadline rather than a fixed window, or move them...

## Impact

A release tag push costs a second 25-minute boundary run on a flake, and the refusal's named log cannot be read to tell a flake from a fault.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-16 | sdlc-studio | Filed |
