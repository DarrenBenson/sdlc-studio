# BG0968: CI runs tools/tests in the same step as the skill suite, so a red skill suite hides every tools/tests failure

> **Status:** Open
> **Severity:** Medium
> **Points:** 1
> **Affects:** .github/workflows/lint.yml, tools/tests/test_lint_workflow_coverage.py, tools/tests/test_ci_suites_unchained.py
> **Evidence:** Found 2026-10-06/07 during the triage session that filed BG0955-BG0963 in this repository. CI run 37335339814; BG0957.
> **Created:** 2026-10-07
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-10-07T12:36:58Z

## Summary

The Lint workflow's step 'Run the unit suites once' runs `tools/skill-tests.sh` and then `gate.py --boundary push --run-tests tools/tests/test_*.py` in one `run:` block (.github/workflows/lint.yml:88-90). The step's shell stops at the first failing command, so when the skill suite is red, tools/tests never runs and its failures are invisible. Runs 37335339814 (aa19a2e3) and the 2c72fe8e push failed on `test_lean_backlog_sweep` alone; `test_epic_index_derived` had broken at 2c72fe8e as well (BG0957) and no CI run showed it until the local gate did. One red masking another is how a second defect survives the fix of the first.

## Steps to Reproduce

Make any skill-suite test fail; push; the run's 'Run the unit suites once' step fails and its log shows no tools/tests output at all.

## Proposed Fix

Run tools/tests as its own step with `if: success() || failure()`, or run both commands and fail the step on either exit code, so each suite reports on every run.

## Acceptance Criteria

- [ ] **AC1** A failing skill suite no longer prevents tools/tests from running in the same workflow run, and both results are reported
  - **Verify:** pytest tools/tests/test_ci_suites_unchained.py -k tools_tests_run_when_the_skill_suite_fails
- [ ] **AC2** A test fails if the workflow again runs the two suites so that one's failure stops the other
  - **Verify:** pytest tools/tests/test_ci_suites_unchained.py -k suites_are_not_chained

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-07 | sdlc-studio | Filed |
