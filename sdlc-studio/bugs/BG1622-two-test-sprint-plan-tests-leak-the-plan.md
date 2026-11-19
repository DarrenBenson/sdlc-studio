# BG1622: Two test_sprint plan tests leak the plan's new unmetered warning, so a passing full run prints 106 diagnostic lines and the push gate refuses it

> **Status:** Fixed
> **Severity:** High
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/scripts/tests/test_sprint.py, changelog.d/BG1622.md
> **Evidence:** run eighteen, 2026-11-19: push of a5809780 refused by the green-run noise gate on devserver1 (106 above 104); .local/run18/noise-39a74b54.log and noise-a5809780.log; per-line diff of test_sprint at both commits
> **Created:** 2026-11-19
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-19T16:13:43Z

## Summary

BG1605 made `sprint plan --write` warn on stderr when no session token stamp can be taken. Two `test_sprint` tests run plan --write in-process without capturing stderr, so the warning reaches pytest's capture as a diagnostic line: AuthoringPlanTests::`test_plan_write_persists_artifact` and CapacityFeedsTheAppetiteTests::`test_capacity_units_become_the_run_breakers_ceiling.` The full run then prints 106 lines against tools/test-noise-baseline.json's total of 104, and the pre-push boundary gate refuses every push from a5809780 onwards. Reproduced locally on the same 24 modules: 104 lines at 39a74b54 and 106 at a5809780; the only new lines are these two warnings.

## Steps to Reproduce

Run `bash tools/run-suite.sh --noise-gate python3 -m pytest -q .claude/skills/sdlc-studio/scripts/tests/test_sprint.py` at a5809780: `test_sprint` prints 16 lines against its budget of 15, and two of them begin 'warning: no session token stamp could be taken as this run opened'.

## Proposed Fix

Capture stderr in the two tests and assert the warning is said there, so the run still proves the warning and prints nothing. Leave the noise baseline as it is.

## Acceptance Criteria

### AC1: The two plan tests capture the unmetered warning and assert it

- **Given** a workspace with no harness transcript store, as each of the two tests builds
- **When** `test_plan_write_persists_artifact` and `test_capacity_units_become_the_run_breakers_ceiling` run `sprint plan --write`
- **Then** each test captures the plan's stderr and asserts it carries the warning that no session token stamp could be taken, and nothing of it reaches pytest's capture
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::AuthoringPlanTests::test_plan_write_persists_artifact .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::CapacityFeedsTheAppetiteTests::test_capacity_units_become_the_run_breakers_ceiling
- **Verified:** yes (2026-11-19)

### AC2: A passing test_sprint run is back within its noise budget

- **Given** tools/test-noise-baseline.json, unchanged
- **When** test_sprint.py runs under the green-run noise gate
- **Then** it prints no line beginning `warning: no session token stamp`, and the selected run is within the module's budget
- **Verify:** shell bash tools/run-suite.sh --noise-gate python3 -m pytest -q -p no:cacheprovider .claude/skills/sdlc-studio/scripts/tests/test_sprint.py
- **Verified:** yes (2026-11-19)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-19 | sdlc-studio | Filed |
