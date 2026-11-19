# BG1587: A commit that adds a test file never selects test_test_census.py, whose guards scan every test file, so a new hand-copied script list is first seen by the full suite at push

> **Status:** Superseded
> **Superseded by:** BG1115
> **Severity:** Low
> **Points:** 2
> **Affects:** .githooks/pre-commit, tools/tests/test_lean_precommit_parallel.py
> **Evidence:** US1313 landed at 4ed7d225 through the commit gate; the push gate refused it on test_test_census.py.
> **Created:** 2026-11-18
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-18T08:57:25Z

## Summary

The commit gate selects test modules from what the staged change imports or names. `test_test_census.py` reads every test file under both suite directories by glob, so no import edge points at it from a new test file, and the commit that added `test_repo_risk_map.py` (US1313) passed its gate while the census guard would have refused it. The push's full suite was the first to run it. The same shape as BG1115 (a subcommand never selecting `test_cli_grammar.py).`

## Steps to Reproduce

Stage a new tools/tests/`test_x.py` holding a literal of three shipped script names and commit: the unit-suites lane does not run `test_test_census.py.` Run it by hand and it fails.

## Proposed Fix

Select `test_test_census.py` whenever a `test_`*.py file under either suite directory is added or changed, as BG1115 proposes for the grammar test.

## Acceptance Criteria

- [ ] **AC1** The behaviour described is corrected: The commit gate selects test modules from what the staged change imports or names.
- [ ] **AC2** Following the recorded steps no longer reproduces the defect: Stage a new tools/tests/`test_x.py` holding a literal of three shipped script names and commit: the unit-suites lane does not run `test_test_census.py.` Run it...
- [ ] **AC3** The proposed fix lands, pinned by a test: Select `test_test_census.py` whenever a `test_`*.py file under either suite directory is added or changed, as BG1115 proposes for the grammar test.

## Impact

A defect a cheap commit lane could catch costs a 14-minute push and a repair lane.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-18 | sdlc-studio | Filed |
