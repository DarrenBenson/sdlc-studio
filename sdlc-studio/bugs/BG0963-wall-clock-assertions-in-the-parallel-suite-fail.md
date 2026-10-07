# BG0963: Wall-clock assertions in the parallel suite fail under load, so a busy machine refuses commits and pushes on timing alone

> **Status:** Open
> **Severity:** Medium
> **Points:** 5
> **Affects:** .claude/skills/sdlc-studio/scripts/tests/test_status.py, .claude/skills/sdlc-studio/scripts/tests/test_lean_test_selection.py, .claude/skills/sdlc-studio/scripts/tests/test_gate.py, .claude/skills/sdlc-studio/scripts/tests/test_mutation.py, .claude/skills/sdlc-studio/scripts/tests/test_lean_lane_yield.py, .claude/skills/sdlc-studio/scripts/tests/test_lean_mutation_ledger_retired.py, .claude/skills/sdlc-studio/scripts/tests/test_lean_release_verify.py, tools/tests/test_lean_precommit_parallel.py, tools/tests/test_test_census.py
> **Evidence:** Push boundary gate on 65e36b98 (2026-10-06, load average 17) and fb1ce886 (2026-10-07, load 21-27); commit hook on c578a919 twice (2026-10-07, load 5-11); each named test passed alone in a clean worktree.
> **Created:** 2026-10-07
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-10-07T12:21:26Z

## Summary

Several tests assert a fixed wall-clock bound or compare output that embeds a measured duration, and they run in the parallel (xdist) partition beside every other module. Under load they fail while the code is correct, and each passes alone. On 2026-10-06 and 2026-10-07 this refused three gate runs and two commits in this repository: the push boundary on 65e36b98 and fb1ce886, and the commit hook twice on c578a919. The classes are: a fixed budget (`test_status` GatherPerformance, the headline under 3.0s, failed at 4.5s and 5.8s; `test_lean_test_selection` selection under 3.0s, failed at 7.0s; `test_gate` ModuleAloneLaneTests, 8 one-second modules under 3.0s, failed at 5.3s; `test_mutation` MutationSeriesRowTests elapsed at least 0.6, read 0.485); a byte comparison of output that prints measured seconds (`test_lean_lane_yield` and `test_lean_mutation_ledger_retired`, '1s of gate' against '0s of gate'); and subprocess verifiers hitting their 300s timeout (`test_lean_release_verify`, `test_lean_precommit_parallel`). A gate that fails on load trains its users to bypass it, which is how this repository's main went unchecked twice in two days.

## Steps to Reproduce

On an 8-core machine with another session's test run holding the load average near 10: git commit a change to `sprint_report.py`, whose selection reaches `test_status` -> refused on GatherPerformanceTests (headline after 4.5s, limit 3.0s); pytest the same test alone -> passes.

## Proposed Fix

Run every wall-clock assertion in the `serial_only` partition, which runs after the parallel pass, or bound it relative to a calibration measured in the same process rather than a fixed constant; normalise measured durations out of any byte-compared output; and add a census check that refuses a parallel-partition test comparing a measured duration against a constant, so the class cannot return.

## Acceptance Criteria

- [ ] **AC1** No test in the parallel partition compares a measured duration against a fixed constant; a census test fails when one does, naming it
  - **Verify:** pytest tools/tests/test_test_census.py::WallClockCensusTests::test_no_parallel_test_bounds_a_measured_duration_by_a_constant
- [ ] **AC2** Output a test compares byte for byte carries no measured duration, or the comparison normalises it, shown by a test that varies the seconds
  - **Verify:** pytest tools/tests/test_test_census.py::WallClockCensusTests::test_compared_output_is_insensitive_to_measured_seconds
- [ ] **AC3** Each timing assertion named here still runs at the push boundary, in the serial partition or against a calibrated bound, and still fails on the slowdown it exists to catch
  - **Verify:** pytest tools/tests/test_test_census.py::WallClockCensusTests::test_the_timing_assertions_still_run_at_the_boundary

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-07 | sdlc-studio | Filed |
