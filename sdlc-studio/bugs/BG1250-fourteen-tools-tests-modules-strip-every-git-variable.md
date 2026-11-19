# BG1250: Fourteen `tools/tests` modules strip every `GIT_*` variable from a child's environment, dropping the conftest's `maintenance.auto` pin and reopening the BG0711 teardown race

> **Status:** Open
> **Severity:** Low
> **Points:** 3
> **Affects:** tools/tests/conftest.py, tools/tests/test_bench_headless.py, tools/tests/test_check_budgets.py, tools/tests/test_corpus_verify_env.py, tools/tests/test_lean_docs_v61.py, tools/tests/test_lean_docs_v63.py, tools/tests/test_lean_gate_docs.py, tools/tests/test_lean_one_runner.py, tools/tests/test_lean_push.py, tools/tests/test_lean_release_cut_v62.py, tools/tests/test_lean_release_cut_v63.py, tools/tests/test_lean_release_notes.py, tools/tests/test_lean_release_notes_v61.py, tools/tests/test_lean_upgrade_page_docs.py, tools/tests/test_remote_gate_doctor.py, tools/tests/test_remote_gate_runs.py, tools/tests/test_run_suite_remote.py, tools/tests/test_skill_tests_env.py, tools/tests/test_git_env_keeps_maintenance_pin.py, changelog.d/BG1250.md
> **Evidence:** run seven (RUN-01M6RAP7) US1128 review round 1
> **Created:** 2026-11-06
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-06T14:37:26Z

## Summary

Run seven, US1128 review round 1 (non-blocking; the reviewer asked for one bug for the class). `test_bench_headless.py`'s `_git_env` (:78-80 at round 1, :113 now) drops every `GIT_*` variable, including the `GIT_CONFIG_COUNT`, `GIT_CONFIG_KEY_0` and `GIT_CONFIG_VALUE_0` the root `conftest.py` sets to turn `maintenance.auto` off (the BG0782 fix). Probed under pytest on git 2.55.0: `maintenance.auto` reads false in the session and unset under `_git_env`, so the module's ten fixture commits can start a detached auto-maintenance that races the temporary directory's teardown (the BG0711 class). `git grep` at 4950f968 finds the same `startswith("GIT_")` filter in 13 more modules: `test_corpus_verify_env.py:62`, `test_lean_docs_v61.py:57`, `test_lean_gate_docs.py:104`, `test_lean_one_runner.py:102`, `test_lean_push.py:109`, `test_lean_release_cut_v62.py:56`, `test_lean_release_notes.py:40`, `test_lean_release_notes_v61.py:55`, `test_lean_upgrade_page_docs.py:78`, `test_remote_gate_doctor.py:79`, `test_remote_gate_runs.py:157`, `test_run_suite_remote.py:79,241` and `test_skill_tests_env.py:99`. No open bug records it.

## Steps to Reproduce

Under pytest, in any of those modules, run `git config --get maintenance.auto` with the environment the module builds: it prints nothing, where the session's own environment prints false.

## Proposed Fix

Add one helper to `tools/tests/conftest.py` that drops the repository-locating variables (`GIT_DIR`, `GIT_WORK_TREE`, `GIT_INDEX_FILE`, `GIT_OBJECT_DIRECTORY`, `GIT_COMMON_DIR` and the like) but keeps `GIT_CONFIG_COUNT` with its `GIT_CONFIG_KEY_n` and `GIT_CONFIG_VALUE_n` pairs, use it in all fourteen modules, and add a guard test that refuses a bare `startswith("GIT_")` environment filter under `tools/tests`.

## Acceptance Criteria

- [ ] **AC1** Given the pytest session's `maintenance.auto` pin, when a module builds a child's environment through the shared `tools/tests/conftest.py` helper, then `git config --get maintenance.auto` prints false in that environment and no repository-locating variable (`GIT_DIR`, `GIT_WORK_TREE`, `GIT_INDEX_FILE`, `GIT_OBJECT_DIRECTORY`, `GIT_COMMON_DIR`) remains. Fails on: a helper that drops `GIT_CONFIG_COUNT` or its key and value pairs, or keeps a repository-locating variable.
  - **Verify:** pytest tools/tests/test_git_env_keeps_maintenance_pin.py::GitEnvKeepsMaintenancePinTests::test_the_helper_keeps_the_config_pin_and_drops_the_repo_locating_variables
- [ ] **AC2** Given the modules under `tools/tests`, when the guard sweeps them, then none holds a bare `startswith("GIT_")` environment filter, and a filter planted in a temporary directory is named by the same sweep. Fails on: a module keeping its own filter, or a sweep that passes the planted one.
  - **Verify:** pytest tools/tests/test_git_env_keeps_maintenance_pin.py::GitEnvKeepsMaintenancePinTests::test_no_module_filters_every_git_variable

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-06 | Claude Opus 5.5 | Filed |
