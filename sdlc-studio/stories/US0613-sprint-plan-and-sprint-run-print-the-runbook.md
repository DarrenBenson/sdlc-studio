# US0613: sprint plan and sprint run PRINT the runbook, and a guard fails when a step names a command that no longer exists

> **Status:** Ready
> **Delivers:** CR0518
> **Created:** 2026-08-01
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py
> **Epic:** EP0202
> **Points:** 5

## User Story

**As a** maintainer relying on the runbook staying true
**I want** the runbook printed at plan time and guarded against naming a command that no longer exists
**So that** it reaches the agent when it is needed and cannot rot into advice for a renamed tool

## Acceptance Criteria

### AC1: sprint plan and sprint run print the runbook

- **Given** either command
- **When** it runs
- **Then** the runbook reaches the output, because a document nobody is made to read is one that gets skipped (LL0027)
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::RunbookTests::test_plan_and_run_print_the_runbook

### AC2: a step naming a missing command fails the guard

- **Given** a runbook step naming a command absent from the shipped surface
- **When** the guard runs
- **Then** it fails naming the step, because a runbook that has rotted is worse than none
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::RunbookTests::test_a_missing_command_fails_the_guard

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-01 | sdlc-studio | Created via `new` (deterministic) |
