# US0351: test_autosprint.py exercising the primary path

> **Status:** Draft
> **Delivers:** CR0337
> **Created:** 2026-07-23
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Epic:** EP0119
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/tests/test_autosprint.py, .claude/skills/sdlc-studio/scripts/autosprint.py

## User Story

**As a** {{role}}
**I want** {{capability}}
**So that** {{benefit}}

## Acceptance Criteria

### AC1: autosprint's primary path is exercised end to end

- **Given** a fixture project with a planned batch
- **When** `autosprint` is driven through its primary path
- **Then** the run opens, the batch is processed and the run closes, with the assertions made on the resulting state rather than on the absence of an exception
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_autosprint.py::PrimaryPathTests::test_the_primary_path_drives_a_batch_to_close

### AC2: a failing unit stops the loop rather than being skipped

- **Given** a batch whose second unit fails
- **When** the loop runs
- **Then** it stops and reports the failing unit, and the units after it are NOT reported as delivered - a loop that swallows a failure manufactures a green sprint
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_autosprint.py::PrimaryPathTests::test_a_failing_unit_stops_the_loop_and_is_named

### AC3: the test fails against the untested module, proving it is not vacuous

- **Given** the test file added here
- **When** a mutant is applied to autosprint's loop control
- **Then** at least one test in this module fails - a first test for an untested module must be shown to bind, or it is coverage theatre
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_autosprint.py::PrimaryPathTests::test_the_suite_kills_a_loop_control_mutant

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-23 | sdlc-studio | Created via `new` (deterministic) |
