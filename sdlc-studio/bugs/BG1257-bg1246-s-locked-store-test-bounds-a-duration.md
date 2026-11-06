# BG1257: BG1246's locked-store test bounds a duration its own process measured without the wall-clock census marks

> **Status:** Fixed
> **Severity:** Medium
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/scripts/tests/test_meter_codex.py, tools/tests/test_test_census.py
> **Evidence:** run eight (RUN-01M6RZQZ) second batch commit, refused by the wall-clock census, 2026-11-06
> **Created:** 2026-11-06
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-06T18:39:39Z

## Summary

`test_meter_codex.py::CodexMeterTests::test_a_locked_store_is_abandoned_within_the_bound` (BG1246, landed in c985273f) asserts the wait stays under a constant bound, which fails on a busy machine and passes alone. `tools/tests/test_test_census.py::WallClockCensusTests::test_no_parallel_test_bounds_a_measured_duration_by_a_constant` refused run eight's second batch for it; the test carries neither `@pytest.mark.serial_only` nor `@pytest.mark.boundary_only`.

## Steps to Reproduce

Run `python3 -m pytest tools/tests/test_test_census.py::WallClockCensusTests -q` at c985273f.

## Proposed Fix

Mark the test `@pytest.mark.serial_only` and `@pytest.mark.boundary_only`, as `test_verify_timeout_reaps.py` does.

## Acceptance Criteria

- [ ] **AC1** No parallel test bounds a duration its own process measured by a constant; `test_a_locked_store_is_abandoned_within_the_bound` runs serially and at the boundary only.
  - **Verify:** pytest tools/tests/test_test_census.py::WallClockCensusTests
  - **Verified:** yes (2026-11-06)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-06 | Claude Opus 5.5 | Filed |
| 2026-11-06 | Claude Opus 5.5 | Criteria authored for run eight |
