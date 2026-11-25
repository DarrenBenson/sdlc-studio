# BG1752: Two prose-escaper tests bound a measured duration by a constant and fail the wall-clock census

> **Status:** Fixed
> **Severity:** Low
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/scripts/tests/test_file_finding.py, changelog.d/BG1752.md
> **Evidence:** the push boundary gate on devserver1 refused 09ec8c22b in run twenty-six (full-suite lane, 1 red)
> **Created:** 2026-11-25
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** RUN-01M87B5M - raised during the run, 2026-11-25T05:53:34Z

## Summary

BG1304's rounds added `MdSafeProseTests::test_no_generated_prose_comes_back_with_two_touching_spans` and `test_the_escaper_is_linear_in_a_paths_segment_count` to `test_file_finding.py`, each asserting a wall-clock bound its own process measured, with neither `serial_only` nor `boundary_only` marked. The wall-clock census (`tools/tests/test_test_census.py`) refuses that, so the push boundary gate on the full suite went red at 09ec8c22b and the push was refused.

## Steps to Reproduce

1. Run `python3 -m pytest tools/tests/test_test_census.py::WallClockCensusTests::test_no_parallel_test_bounds_a_measured_duration_by_a_constant`.
2. It names test_file_finding.py lines 499 and 508.

## Proposed Fix

Mark both tests `@pytest.mark.serial_only` and `@pytest.mark.boundary_only`, or take the clock out of the assertion (count operations instead of seconds), keeping the linear-time and touching-span properties pinned.

## Acceptance Criteria

- [ ] **AC1** Given the full suite, when the wall-clock census runs, then no test in `test_file_finding.py` bounds a duration its own process measured without both markers, and the escaper's linear-time and no-touching-span properties are still pinned. Fails on: the census naming either test.
  - **Verify:** pytest tools/tests/test_test_census.py::WallClockCensusTests::test_no_parallel_test_bounds_a_measured_duration_by_a_constant
  - **Verified:** yes (2026-11-25)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-25 | sdlc-studio | Filed |
