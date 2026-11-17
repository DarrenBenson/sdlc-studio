# BG1310: `tools/skill-tests.sh`, the unittest runner `npm test` uses, loads no conftest, so the harness-variable scrub BG1197 added never runs there and the meter tests fail under a Cursor session

> **Status:** Open
> **Severity:** Medium
> **Points:** 2
> **Affects:** tools/skill-tests.sh, conftest.py, tools/tests/test_skill_tests_env.py
> **Evidence:** The run nine US0986 builder's hand-back (2026-11-09): the CURSOR_AGENT=1 and CLAUDECODE=1 runs of the 14 modules through tools/skill-tests.sh
> **Created:** 2026-11-09
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5; human; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-09T13:40:54Z

## Summary

Found rebuilding US0986 with BG1205 in run nine (2026-11-09). BG1197's root conftest.py clears the harness variables before any meter test runs, so under pytest the suite no longer depends on the harness running it (382 passed; 88 failed with `--noconftest`). `tools/skill-tests.sh` runs the skill's tests through unittest, which loads no conftest, so the scrub never runs: with `CURSOR_AGENT`=1 set, the 14 meter-reaching modules other than `test_token_meters.py` and `test_meter_cursor.py` give 74 failures and 14 errors, and pass with CLAUDECODE=1. A contributor running `npm test` from a Cursor, Copilot or OpenCode session sees a red suite that the push gate (pytest) shows green.

## Steps to Reproduce

1. Export `CURSOR_AGENT`=1 in a shell.
2. Run `bash tools/skill-tests.sh`.
3. The meter-reaching modules fail (74 failures, 14 errors); the same run with CLAUDECODE=1 passes.

## Proposed Fix

Have the unittest runner apply the same harness-variable scrub the conftest applies before it loads any test module (one shared helper both call), and add a test that runs one meter-reaching module through the runner with `CURSOR_AGENT` set and sees it pass.

## Acceptance Criteria

- [ ] **AC1** Given a shell that exports `CURSOR_AGENT=1`, when a meter-reaching test module is run through `tools/skill-tests.sh`, then it passes as it does under pytest. Fails on: the runner handing the caller's harness variable to the tests, so a Claude transcript fixture is read by the Cursor meter.
  - **Verify:** pytest tools/tests/test_skill_tests_env.py::HarnessScrubTests::test_a_meter_module_passes_through_the_runner_with_cursor_agent_set
- [ ] **AC2** Given a shell that exports `CLAUDECODE=1` and one variable the fixtures own, when the runner starts its child, then the child sees none of the names `token_meters.selection_variables()` lists and still sees the fixture's variable. Fails on: a scrub that omits a harness, or one that clears a variable the tests set for themselves.
  - **Verify:** pytest tools/tests/test_skill_tests_env.py::HarnessScrubTests::test_the_runner_clears_every_selection_variable_and_nothing_else
- [ ] **AC3** Given the root `conftest.py` and `tools/skill-tests.sh`, when the names each clears are read, then both come from one helper, so a harness added to the meter is cleared by both runners. Fails on: a second hand-written list in the runner that drifts from the conftest's.
  - **Verify:** pytest tools/tests/test_skill_tests_env.py::HarnessScrubTests::test_the_runner_and_the_conftest_clear_the_same_names_from_one_helper

## Further evidence

- 2026-11-12 (RUN-01M77177, qa-seat-US1014-r1): three US1012 and US1016 tests fail under `npm test` (tools/skill-tests.sh) in a Claude Code shell, because harness detection reads the shell's environment; they pass under pytest and on the gate host.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-09 | Claude Opus 5.5 | Filed |
