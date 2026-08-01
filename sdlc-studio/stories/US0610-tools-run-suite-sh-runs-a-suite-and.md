# US0610: tools/run-suite.sh runs a suite and writes exit_code, counts, duration and head_sha to sdlc-studio/.local/suite-verdict.json, printing only the verdict line

> **Status:** Review
> **Delivers:** CR0519
> **Created:** 2026-08-01
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** tools/run-suite.sh, tools/tests/test_run_suite.py, .githooks/pre-commit
> **Epic:** EP0201
> **Points:** 5

## User Story

**As a** agent reporting whether a suite passed
**I want** the verdict written to a file rather than printed into a stream I have to interpret
**So that** a red suite can never be read as green because a pipe swallowed the exit code

## Acceptance Criteria

### AC1: the wrapper writes a verdict file

- **Given** `tools/run-suite.sh scripts|tools|all`
- **When** it finishes
- **Then** `sdlc-studio/.local/suite-verdict.json` carries suite, exit_code, passed, failed, duration and head_sha, and only the verdict line is printed - so there is nothing worth piping to `tail`
- **Verify:** pytest tools/tests/test_run_suite.py::VerdictFileTests::test_the_wrapper_writes_the_verdict
- **Verified:** yes (2026-08-01)

### AC2: a red run writes a red verdict

- **Given** a suite that fails
- **When** the wrapper runs
- **Then** the file records a non-zero exit_code, because a wrapper that always writes zero reproduces the defect it replaces
- **Verify:** pytest tools/tests/test_run_suite.py::VerdictFileTests::test_a_red_run_writes_a_red_verdict
- **Verified:** yes (2026-08-01)

### AC3: the verdict records the HEAD it was taken at

- **Given** a verdict written at one commit and read at another
- **When** it is read
- **Then** the recorded sha makes a stale verdict distinguishable from a current one
- **Verify:** pytest tools/tests/test_run_suite.py::VerdictFileTests::test_the_verdict_records_its_head
- **Verified:** yes (2026-08-01)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-01 | sdlc-studio | Created via `new` (deterministic) |
