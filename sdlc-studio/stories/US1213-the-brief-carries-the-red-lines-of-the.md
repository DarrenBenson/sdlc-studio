# US1213: The brief carries the red lines of the verifier dry run and the selected tests, stamped with its HEAD

> **Status:** Draft
> **Risk-class:** high
> **Delivers:** CR0679
> **Created:** 2026-11-17
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/critic.py, .claude/skills/sdlc-studio/scripts/gate.py, .claude/skills/sdlc-studio/scripts/tests/test_critic_brief_results.py, .claude/skills/sdlc-studio/scripts/tests/test_gate.py
> **Epic:** EP0331
> **Points:** 5
> **Persona:** Abena Osei

## User Story

**As a** Abena Osei
**I want** The brief carries the red lines of the verifier dry run and the selected tests, stamped with its HEAD
**So that** CR0679 is delivered by work that can be planned and checked

## Acceptance Criteria

### AC1: The brief prints the red criteria, stamped with the commit it ran at

- **Given** a unit with one criterion whose verifier passes and one whose verifier fails, and a second unit whose criteria all pass
- **When** `critic.py brief --unit <id> --seat qa` is run for each
- **Then** the first brief carries a RESULTS section that names the HEAD commit it ran at and lists the failing criterion with the verifier's own failure line, and does not list the passing one; the second says in one line that all of its criteria were green at that commit. Fails on: a brief that carries the verify command and no result, or a RESULTS section listing green lines
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic_brief_results.py::BriefResultsTests::test_results_list_only_the_red_criteria_at_the_head_they_ran_at

### AC2: The gate's selected tests for the Affects are run and a red one is listed

- **Given** a unit whose Affects names a script whose mapped test module holds a failing test
- **When** `critic.py brief --unit <id> --seat qa` is run
- **Then** the RESULTS section lists that failing test by node id, and the modules it ran are the ones the gate selects for the same paths. Fails on: a selection made by the brief's own rule, which can differ from the gate's, or a failing selected test left out
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_gate.py::BriefSelectionTests::test_the_selection_for_a_units_affects_is_the_gates_own

### AC3: Taking the brief writes nothing to the unit or the verify report

- **Given** a unit file and a verify report whose bytes are recorded
- **When** `critic.py brief --unit <id> --seat qa` is run
- **Then** the unit's file and the verify report are byte-identical afterwards. Fails on: a Verified stamp or a report entry written by a reviewer's brief
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic_brief_results.py::BriefResultsTests::test_the_brief_writes_nothing_to_the_unit_or_the_report

### AC4: A verifier that cannot run is reported, never read as green

- **Given** a unit one of whose Verify lines names a test file that does not exist
- **When** `critic.py brief --unit <id> --seat qa` is run
- **Then** the brief is still issued and its RESULTS section names that criterion as not run with the reason. Fails on: the criterion counted as green, or the brief refused
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic_brief_results.py::BriefResultsTests::test_a_verifier_that_cannot_run_is_named_not_run

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-17 | sdlc-studio | Created via `new` (deterministic) |
