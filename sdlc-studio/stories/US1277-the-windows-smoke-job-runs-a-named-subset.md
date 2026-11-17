# US1277: The Windows smoke job runs a named subset of the script tests and fails when one fails

> **Status:** Draft
> **Risk-class:** standard
> **Delivers:** CR0719
> **Created:** 2026-11-17
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .github/workflows/lint.yml, tools/tests/test_lint_workflow_coverage.py
> **Epic:** EP0358
> **Points:** 3
> **Persona:** Rowan Achterberg

## User Story

**As a** Rowan Achterberg
**I want** The Windows smoke job runs a named subset of the script tests and fails when one fails
**So that** CR0719 is delivered by work that can be planned and checked

## Acceptance Criteria

### AC1: The Windows job runs named script tests with Python

- **Given** the `windows-smoke` job in `.github/workflows/lint.yml`
- **When** its steps are read
- **Then** the job sets up Python and has a step that runs the script tests by name: an explicit list of test modules or test ids, not a discovery of the whole tree, and every name on the list resolves to a test file that exists. Fails on: the job as it stands, which runs no Python, or a list naming a module that was renamed or deleted
- **Verify:** pytest tools/tests/test_lint_workflow_coverage.py::WindowsSmokeScriptTests::test_the_job_runs_a_named_subset_that_exists

### AC2: A failing test fails the job

- **Given** the step that runs the named subset
- **When** its shell, its commands and its settings are read
- **Then** the test run's exit status is the step's: the step carries no `continue-on-error`, no command after the test run can replace its status, and no `|| true` or equivalent discards it. Fails on: a PowerShell step where a later command's exit code is the one the runner reads, so a red test run reports green
- **Verify:** pytest tools/tests/test_lint_workflow_coverage.py::WindowsSmokeScriptTests::test_a_failing_test_run_is_the_steps_exit_status

### AC3: The named subset covers the cleanup paths fixed for Windows

- **Given** the subset the job names and the tests that hold the group-kill cleanup in `verify_ac.py` and `mutation.py`
- **When** the two are compared
- **Then** the subset includes both of those tests, so the paths the request found by reading are run on a Windows host. Fails on: a subset of trivial tests that would pass while acceptance-criteria verification still raises on Windows
- **Verify:** pytest tools/tests/test_lint_workflow_coverage.py::WindowsSmokeScriptTests::test_the_subset_includes_the_group_kill_cleanup_tests

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-17 | sdlc-studio | Created via `new` (deterministic) |
