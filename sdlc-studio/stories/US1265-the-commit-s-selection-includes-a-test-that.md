# US1265: The commit's selection includes a test that runs other test modules by path when one of those modules is staged

> **Status:** Draft
> **Risk-class:** high
> **Delivers:** CR0713
> **Created:** 2026-11-17
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/gate.py, .claude/skills/sdlc-studio/scripts/tests/test_lean_test_selection.py, tools/tests/test_lean_release_notes.py
> **Epic:** EP0353
> **Points:** 3
> **Persona:** Abena Osei

## User Story

**As a** Abena Osei
**I want** The commit's selection includes a test that runs other test modules by path when one of those modules is staged
**So that** CR0713 is delivered by work that can be planned and checked

## Acceptance Criteria

### AC1: A staged module selects the test that runs it by path

- **Given** a throwaway repository with a test module `test_runner.py` that executes other test modules by path, and a test module `test_reader.py` that is one of them
- **When** `gate.select_tests` is asked what a commit staging only `test_reader.py` runs
- **Then** the selectors hold both `test_reader.py` and `test_runner.py`. Fails on: a selection that runs the staged module alone and leaves its runner to the push gate
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_test_selection.py::SelectionTests::test_a_staged_module_selects_the_test_that_runs_it_by_path

### AC2: A module no runner executes selects no runner

- **Given** the same repository and a third test module the runner does not execute
- **When** a commit stages only that module
- **Then** the selectors hold that module and not `test_runner.py`, and the selection adds no new lane, sweep or baseline. Fails on: every commit that touches a test paying for every runner, which is a new check that retires nothing
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_test_selection.py::SelectionTests::test_a_module_no_runner_executes_selects_no_runner

### AC3: The recorded hit no longer reproduces in this repository

- **Given** this repository, where `FrozenNotesTests` in `tools/tests/test_lean_release_notes.py` runs every notes reader by path
- **When** the selection is asked what staging `tools/tests/test_lean_release_notes_v64.py` alone runs
- **Then** the selectors include `tools/tests/test_lean_release_notes.py`. Fails on: the selection at grooming, which returns the v64 module and not the runner that went red at the push boundary on US1170
- **Verify:** pytest tools/tests/test_lean_release_notes.py::FrozenNotesTests::test_staging_a_notes_reader_selects_this_module

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-17 | sdlc-studio | Created via `new` (deterministic) |
