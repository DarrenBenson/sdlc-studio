# BG0727: check_script_tests sweeps two fixed globs, so a script in any other scripts subdirectory needs no test

> **Status:** Superseded
> **Closed with findings in:** Superseded by US0902 (RUN-01M39MC0), which deleted tools/check_script_tests.py and its lane; there is no longer a checker to sweep two fixed globs.
> **Severity:** Medium
> **Points:** 2
> **Affects:** tools/check_script_tests.py, tools/tests/test_check_script_tests.py
> **Created:** 2026-09-21
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

BG0463 claim 19, still true. The guard globs `scripts/*.py` and `scripts/lib/*.py` and nothing else, so `scripts/hooks/` is unswept. It is benign today - `scripts/hooks/close_guard.py` is its only inhabitant and does have a partner test - which is exactly why it will stay unnoticed until the second file lands there. An enumerated list silently exempts whatever it forgot, which this project already carries as a lesson.

## Steps to Reproduce

1. Add a script under `.claude/skills/sdlc-studio/scripts/hooks/` with no partner test. 2. Run `python3 tools/check_script_tests.py`. 3. Clean.

## Proposed Fix

Walk `scripts/` recursively rather than by two fixed globs, excluding `tests/` and `__pycache__`. Pin with a fixture placing an untested script in a subdirectory the old globs missed.

## Acceptance Criteria

### AC1: a script anywhere under scripts/ needs a partner test

- **Given** an untested script placed in a subdirectory neither of the two fixed globs reaches, such as `scripts/hooks/`
- **When** `check_script_tests` runs
- **Then** it is reported, because the sweep walks `scripts/` recursively rather than by an enumerated list of directories
- **Mutant:** in `tools/check_script_tests.py`, keep the two fixed globs - the guard is then clean on a script in any other subdirectory, which is how an enumerated list silently exempts what it forgot
- **Verify:** manual - retired by US0902: the script-tests lane and its checker were deleted; the TSD map is prose review keeps
- **Verified:** manual (2026-09-24) - retired, superseded by US0902

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-21 | sdlc-studio | Filed |
| 2026-09-24 | Claude Opus 5.5 | Superseded by US0902: the checker is deleted |
