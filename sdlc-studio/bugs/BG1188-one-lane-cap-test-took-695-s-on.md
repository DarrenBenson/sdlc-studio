# BG1188: One lane-cap test took 695 s on a worker, re-running its whole class once per hook lane

> **Status:** Open
> **Severity:** Low
> **Points:** 2
> **Affects:** tools/tests/test_lean_commit_lanes.py, changelog.d/BG1188.md
> **Evidence:** US1112 builder report, xdist batch per-node durations (2026-11-03).
> **Created:** 2026-11-03
> **Created-by:** sdlc-studio file
> **Raised-by:** claude; human; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-03T03:24:38Z

## Summary

2026-11-03, US1112's build (run five). `tools/tests/test_lean_commit_lanes.py::LaneCapTests::test_dropping_any_one_listed_lane_leaves_the_cap_tests_green` (line 782) deletes each lane either hook lists in turn and runs every other test in its class against that copy. In US1112's release batch it took 695 s on one xdist worker, the longest single test there. No Done criterion names it, but the push gate's full suite pays for it on every push.

## Steps to Reproduce

1. `time python3 -m pytest -q 'tools/tests/test_lean_commit_lanes.py::LaneCapTests::test_dropping_any_one_listed_lane_leaves_the_cap_tests_green'`.

## Proposed Fix

Check each dropped lane against the cap tests' lane references directly, or run the class once and read every lane name it touches, so the cost does not scale with lanes times tests.

## Acceptance Criteria

- [ ] **AC1** The test finishes inside 120 s on this repository and still fails when a cap test names a lane that one hook's `--list` prints.
  - **Verify:** shell timeout 120 python3 -m pytest -q tools/tests/test_lean_commit_lanes.py::LaneCapTests::test_dropping_any_one_listed_lane_leaves_the_cap_tests_green

## Impact

The longest single test in the suite sets a floor under the push gate and the release lane on any number of cores.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-03 | claude | Filed |
