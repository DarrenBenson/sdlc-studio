# US1178: A stale private root left by a killed run and owned by no live process is removed and named when the next run starts

> **Status:** Draft
> **Risk-class:** standard
> **Delivers:** CR0637
> **Created:** 2026-11-17
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** conftest.py, tools/skill-tests.sh, tools/tests/test_suite_stale_root.py
> **Epic:** EP0318
> **Points:** 2
> **Persona:** Abena Osei

## User Story

**As a** Abena Osei
**I want** A stale private root left by a killed run and owned by no live process is removed and named when the next run starts
**So that** CR0637 is delivered by work that can be planned and checked

## Acceptance Criteria

### AC1: A root whose owning process is gone is removed and named

- **Given** a `sdlc-tests-` root beside the place the new run's root is made, left by a run that was killed: the process recorded as its owner is no longer alive
- **When** the next pytest session starts through `conftest.py`
- **Then** the stale root is removed before the session's tests run and one line of output names the directory removed. Fails on: the stale root left in place, or removed with no line naming it
- **Verify:** pytest tools/tests/test_suite_stale_root.py::SuiteStaleRootTests::test_a_root_whose_owner_is_dead_is_removed_and_named

### AC2: A live run's root and an unrelated directory are left alone

- **Given** beside the new run's root, a `sdlc-tests-` root whose recorded owner is a live process (a concurrent run), and a directory that is not a suite root
- **When** a pytest session starts
- **Then** both are still present with their content afterwards and neither is named as removed. Fails on: a sweep by name prefix or by age alone that deletes a concurrent run's fixtures under it
- **Verify:** pytest tools/tests/test_suite_stale_root.py::SuiteStaleRootTests::test_a_live_runs_root_and_an_unrelated_directory_are_kept

### AC3: The shell runner sweeps its own stale roots by the same rule

- **Given** a stale `sdlc-tests.` run directory made by `tools/skill-tests.sh` whose owner is dead, beside one whose owner is alive
- **When** `tools/skill-tests.sh` starts
- **Then** the dead run's directory is removed and named on stderr and the live one is kept. Fails on: only the roots pytest made being swept, so a killed shell run still leaks its tree
- **Verify:** pytest tools/tests/test_suite_stale_root.py::SuiteStaleRootTests::test_the_shell_runner_sweeps_its_own_stale_roots

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-17 | sdlc-studio | Created via `new` (deterministic) |
