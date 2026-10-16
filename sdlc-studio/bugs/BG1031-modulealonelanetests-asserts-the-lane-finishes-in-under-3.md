# BG1031: ModuleAloneLaneTests asserts the lane finishes in under 3.0 seconds of wall clock, so it fails whenever the full parallel suite or another workload shares the cores

> **Status:** Fixed
> **Severity:** Medium
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/tests/test_gate.py, changelog.d/BG1031.md
> **Created:** 2026-10-13
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5 (triage); human; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-10-13T08:44:03Z

## Summary

`test_gate.py::ModuleAloneLaneTests::test_the_push_boundary_runs_every_module_alone_and_names_the_one_that_fails` (`test_gate.py`:5045) times the module-alone lane over one one-second sleeper module per core and asserts `secs < 3.0`. It runs inside the full suite, which already has every core busy with xdist workers, so the bound measures the machine's load, not the pool's size. On devserver1 (8 cores, shared with a self-hosted CI runner) it failed at 3.0 s on 2026-10-12 and at 5.2 s on 2026-10-13 (load average 10.6), each time on a tree whose diff did not touch gate.py, and passed on reruns. A push gate that goes red on the machine's load is one people learn to bypass.

## Steps to Reproduce

Run the full suite on an 8-core host while other work holds the cores: the test fails with 'the lane took N s over 8 one-second modules - serial, or a pool smaller than the cores?'.

## Proposed Fix

Assert the property, not a wall-clock figure: the lane's pool has as many workers as the cores (the summary already prints the pool size), or the sleepers overlap (their recorded start times interleave), so a serial lane still fails and a loaded machine does not.

## Acceptance Criteria

- [ ] **AC1** Given the module-alone lane run on a machine whose cores are all busy, when the test runs, then it passes, because it judges overlap or pool size rather than elapsed seconds
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_gate.py -k test_the_push_boundary_runs_every_module_alone_and_names_the_one_that_fails
  - **Verified:** yes (2026-10-13)
- [ ] **AC2** Given the lane made serial (a pool of one), when the test runs, then it fails
  - **Verify:** manual: the reviewer runs the test with the lane's pool forced to one worker and sees it fail

## Impact

The push gate turns red on a loaded machine for a reason unrelated to the change, and every such red is a push held or a bypass argued for.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-13 | Claude Opus 5.5 (triage) | Filed |
