# US1204: The hostile kit proves a batch obeys a consumer's pytest addopts and collects under warnings as errors

> **Status:** Draft
> **Risk-class:** high
> **Delivers:** CR0675
> **Created:** 2026-11-17
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/gate.py, .claude/skills/sdlc-studio/scripts/tests/test_verifier_hostile_pytest_config.py
> **Epic:** EP0328
> **Points:** 2
> **Persona:** Abena Osei

## User Story

**As a** Abena Osei
**I want** The hostile kit proves a batch obeys a consumer's pytest addopts and collects under warnings as errors
**So that** CR0675 is delivered by work that can be planned and checked

## Acceptance Criteria

### AC1: A batch obeys the consumer's addopts mark expression

- **Given** a scratch consumer tree whose `pytest.ini` sets `addopts = -m "not slow"`, with a unit whose Verify line names a passing test marked slow
- **When** the unit's criteria are run as a batch through the release verify lane and once per criterion
- **Then** both runs give the criterion the same result, the one a plain `pytest <selector>` in that tree gives: the test is deselected and the criterion is not read green. Fails on: a batch whose own `-m` replaces the project's, the recorded mutant of US1112, so the batch runs a test the project deselects
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_verifier_hostile_pytest_config.py::HostilePytestConfigTests::test_a_batch_obeys_the_projects_addopts_mark_expression

### AC2: Collection under warnings as errors equals a fresh collect

- **Given** a scratch consumer tree with `filterwarnings = error` in `pytest.ini` and a `pytest11` entry-point plugin installed on its path
- **When** the runner collects the tree's node ids through its collection server
- **Then** the node ids equal those a fresh `pytest --collect-only -q` prints in that tree, and a stamped criterion on a passing test is read as verified. Fails on: a collection server that imports the plugin before pytest can rewrite it, so the collection fails and a real test reads as missing (BG1183's round-one finding)
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_verifier_hostile_pytest_config.py::HostilePytestConfigTests::test_collection_under_warnings_as_errors_equals_a_fresh_collect

### AC3: The module is selected by a change to the verifier core and stays quick

- **Given** the commit gate's test selection and this module
- **When** the selection is asked for a staged change to `verify_ac.py`, to `gate.py` and to `lib/run_state.py`, and the module is run
- **Then** the module is selected for each of the three, opens no network connection and finishes in under 10 seconds, its share of the kit's 30. Fails on: a kit nothing runs when the verifier core changes, or one too slow to stay in a commit's selection
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_verifier_hostile_pytest_config.py::HostilePytestConfigTests::test_the_module_is_selected_by_the_verifier_core_and_is_quick

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-17 | sdlc-studio | Created via `new` (deterministic) |
