# BG1212: US0989's AC2 test bounds a duration its own process measured, so the push gate's wall-clock census fails on it

> **Status:** Open
> **Severity:** Medium
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/scripts/tests/test_meter_cursor.py, changelog.d/BG1212.md
> **Evidence:** Push gate at cc758984 on devserver1, boundary-suite-last.log.
> **Created:** 2026-11-04
> **Created-by:** sdlc-studio file
> **Raised-by:** claude; human; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-04T16:48:41Z

## Summary

2026-11-04, the push gate at cc758984 (run five). tools/tests/`test_test_census.py`::WallClockCensusTests::`test_no_parallel_test_bounds_a_measured_duration_by_a_constant` named `test_meter_cursor.py`::CursorCloudTests::`test_no_key_no_call_and_failures_not_attributable`:239, which asserts `time.monotonic() - began < 2.0` in a test a parallel commit run executes. Such a test fails on a busy machine and passes alone.

## Steps to Reproduce

1. `python3 -m pytest -q tools/tests/test_test_census.py::WallClockCensusTests::test_no_parallel_test_bounds_a_measured_duration_by_a_constant`.

## Proposed Fix

Move the clock half of AC2's test into its own test marked `serial_only` and `boundary_only`, keeping AC2's test, which `verify_ac` runs, clock-free.

## Acceptance Criteria

- [ ] **AC1** The wall-clock census names no test in `test_meter_cursor.py`, and the worker-joined-with-no-timeout mutant still fails a test.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_meter_cursor.py

## Impact

The push gate is red, and AC2's own test can fail under load.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-04 | claude | Filed |
