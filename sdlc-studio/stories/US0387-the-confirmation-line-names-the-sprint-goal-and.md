# US0387: the confirmation line names the Sprint Goal and the --goal rung distinctly, a test drives both cases

> **Status:** Draft
> **Delivers:** CR0387
> **Created:** 2026-07-23
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Epic:** EP0143
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_run_opened_line.py

## User Story

**As a** operator opening a run with a Sprint Goal
**I want** the run-opened confirmation line to name the Sprint Goal and the `--goal` ladder rung distinctly
**So that** I do not read `goal=unset` as my Sprint Goal failing to take and re-plan against an already-open run

## Acceptance Criteria

### AC1: the confirmation line names the two fields distinctly

- **Given** a run opened by `sprint plan --write`
- **When** the run-opened confirmation line renders
- **Then** it labels the Sprint Goal and the `--goal` ladder rung with distinct names, so neither can be read as the other
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_run_opened_line.py::RunOpenedLine::test_names_sprint_goal_and_rung_distinctly

### AC2: a supplied Sprint Goal shows as set

- **Given** `sprint plan --write --sprint-goal '<text>'`
- **When** the confirmation line renders
- **Then** the Sprint Goal is shown as set, not reported as unset under the rung field's name
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_run_opened_line.py::RunOpenedLine::test_supplied_sprint_goal_shown_as_set

### AC3: an absent Sprint Goal is stated as unset

- **Given** a run opened without `--sprint-goal`
- **When** the confirmation line renders
- **Then** it states the Sprint Goal is unset, since the workflow requires one and never invents it
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_run_opened_line.py::RunOpenedLine::test_absent_sprint_goal_stated

### AC4: the two cases cannot render identically

- **Given** the plan driven both with and without `--sprint-goal`
- **When** the two confirmation lines are compared
- **Then** the text differs, so a regression cannot make the set and unset cases render the same
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_run_opened_line.py::RunOpenedLine::test_with_and_without_sprint_goal_differ

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-23 | sdlc-studio | Created via `new` (deterministic) |
