# BG1086: run-suite.sh's passed count needs bc, which is not a declared prerequisite, and is null with a broken-pipe error where bc is absent

> **Status:** Open
> **Severity:** Low
> **Points:** 1
> **Affects:** tools/run-suite.sh, tools/tests/test_run_suite.py, tools/tests/test_run_suite_counts.py, changelog.d/BG1086.md
> **Evidence:** 2026-10-19, studypc2 (no bc) and the US1078 fixture host: 'paste: write error: Broken pipe', 'suite all: GREEN (null passed, 1s)'. `git log -S'paste -sd+ - | bc'` names ba3bffa2 (BG0579).
> **Created:** 2026-10-19
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-10-19T16:32:41Z

## Summary

run-suite.sh sums pytest's `N passed` counts with `paste -sd+ - | bc`. bc is not on this workstation and is named nowhere in `gate_prereqs.py`, so every verdict records `passed: null` and each run prints `paste: write error: Broken pipe`. The exit code and the failed count are unaffected.

## Steps to Reproduce

On a machine without bc, run `tools/run-suite.sh tools` -> 'GREEN (null passed, ...)' and a broken-pipe line; the verdict's passed is null.

## Proposed Fix

Sum the counts with awk or bash arithmetic instead of bc.

## Acceptance Criteria

- [ ] **AC1** Given a PATH with no bc, when run-suite.sh runs a green suite, then the verdict records the passed count and nothing is printed about a broken pipe
  - **Verify:** pytest tools/tests/test_run_suite_counts.py::RunSuiteCountTests::test_passed_count_without_bc

## Impact

A verdict cannot say how many tests passed on a machine without bc, and the run prints a spurious error.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-19 | Claude Opus 5.5 | Filed |
