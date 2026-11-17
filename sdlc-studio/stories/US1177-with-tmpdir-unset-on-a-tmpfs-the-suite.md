# US1177: With TMPDIR unset on a tmpfs the suite's private root is made on disk and named, and an explicit TMPDIR is honoured

> **Status:** Draft
> **Risk-class:** standard
> **Delivers:** CR0637
> **Created:** 2026-11-17
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** conftest.py, tools/skill-tests.sh, CONTRIBUTING.md, tools/tests/test_suite_temp_root.py
> **Epic:** EP0318
> **Points:** 3
> **Persona:** Abena Osei

## User Story

**As a** Abena Osei
**I want** With TMPDIR unset on a tmpfs the suite's private root is made on disk and named, and an explicit TMPDIR is honoured
**So that** CR0637 is delivered by work that can be planned and checked

## Acceptance Criteria

### AC1: Unset TMPDIR on a tmpfs puts the private root on disk and says where

- **Given** TMPDIR unset and the default temporary directory on a tmpfs (the filesystem probe is stubbed to answer tmpfs, so the test does not depend on the machine it runs on)
- **When** a pytest session starts through the repository's `conftest.py`
- **Then** the private `sdlc-tests-` root is created under the documented disk-backed default in the user's cache directory (`XDG_CACHE_HOME` when set, otherwise `~/.cache`), TMPDIR and `SDLC_TEST_TMPDIR` both name it, and one line of the run's output names the directory. Fails on: a root made under the tmpfs, or a root moved with no line saying where
- **Verify:** pytest tools/tests/test_suite_temp_root.py::SuiteTempRootTests::test_unset_tmpdir_on_a_tmpfs_roots_the_run_on_disk_and_names_it

### AC2: An explicit TMPDIR is honoured unchanged, tmpfs or not

- **Given** TMPDIR set explicitly to a directory the probe reports as a tmpfs; and, as the control, TMPDIR unset with a default temporary directory that is not a tmpfs
- **When** a pytest session starts through `conftest.py`
- **Then** in the first case the private root is created inside the named TMPDIR and nothing is created under the cache default; in the control the root is made under the default temporary directory as it is today. Fails on: an explicit TMPDIR overridden because it is a tmpfs, or every run moved to the cache whatever /tmp is
- **Verify:** pytest tools/tests/test_suite_temp_root.py::SuiteTempRootTests::test_an_explicit_tmpdir_is_honoured_and_a_disk_backed_default_is_left_alone

### AC3: The shell runner places its root by the same rule

- **Given** `tools/skill-tests.sh` started once with TMPDIR unset and the probe answering tmpfs, and once with an explicit TMPDIR
- **When** the script makes its run directory
- **Then** the first run's directory is under the same cache default `conftest.py` uses and is named on stderr, and the second is inside the explicit TMPDIR; a pytest run nested in either finds the directory already owned and makes no second root. Fails on: the shell runner and `conftest.py` disagreeing about where the root goes
- **Verify:** pytest tools/tests/test_suite_temp_root.py::SuiteTempRootTests::test_the_shell_runner_roots_its_run_by_the_same_rule

### AC4: CONTRIBUTING names the default and says an explicit TMPDIR wins

- **Given** CONTRIBUTING.md's section on running the suite
- **When** a contributor reads it
- **Then** it names the disk-backed default directory, read by the test from the constant `conftest.py` uses and not retyped, and says an explicit TMPDIR is honoured. Fails on: a documented path the code does not use, or no mention of the default at all
- **Verify:** pytest tools/tests/test_suite_temp_root.py::SuiteTempRootTests::test_contributing_names_the_default_the_code_uses

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-17 | sdlc-studio | Created via `new` (deterministic) |
