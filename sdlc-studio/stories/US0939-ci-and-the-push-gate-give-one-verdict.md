# US0939: CI and the push gate give one verdict on tools/tests, because both run it the same way

> **Status:** Done
> **Created:** 2026-09-25
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .github/workflows/lint.yml, package.json, tools/run-suite.sh, .claude/skills/sdlc-studio/scripts/gate.py, tools/tests/test_lean_python_floor.py, tools/tests/test_lean_one_runner.py, changelog.d/US0939.md, .claude/skills/sdlc-studio/help/gate.md
> **Epic:** EP0265
> **Points:** 2
> **Persona:** Maya Okafor

## User Story

**As a** founder-engineer pushing to main
**I want** CI to run tools/tests through the same pytest plan the push gate runs, with pytest-xdist installed
**So that** a push the gate passed is not red on CI for a runner difference, and main is read green or red once

## Acceptance Criteria

- **AC1:** Given `lint.yml`, `npm run test:tools` and `tools/run-suite.sh tools`, then each runs tools/tests through `gate.py --boundary push --run-tests tools/tests/test_*.py`, and no step runs `unittest discover -s tools/tests`. Fails on: HEAD (`lint.yml` suite step, `package.json` test:tools, `run-suite.sh` 216-217); changing CI alone, which leaves the local and CI commands different
  - **Verify:** pytest tools/tests/test_lean_one_runner.py::OneRunnerTests::test_ci_and_local_run_tools_tests_through_the_push_plan
  - **Verified:** yes (2026-09-25)
- **AC2:** Given a fixture tools/tests tree holding BG0770's pair (an importer whose `tearDownModule` deletes a directory a sibling module's global still points at), when CI's command read from `lint.yml` and the push's full-suite lane each run over it, then both return the same verdict. Fails on: HEAD, where CI's `unittest discover` reports red and the push's pytest reports green (BG0770, measured)
  - **Verify:** pytest tools/tests/test_lean_one_runner.py::OneRunnerTests::test_ci_and_push_agree_on_a_shared_global_fixture
  - **Verified:** yes (2026-09-25)
- **AC3:** Given `gate.py --run-tests` with `--boundary push`, then the `boundary_only` tests run, and without a boundary they are still left to the push. Fails on: routing CI through the commit's selection path, which silently drops every `boundary_only` test from CI
  - **Verify:** pytest tools/tests/test_lean_one_runner.py::OneRunnerTests::test_a_boundary_run_keeps_boundary_only_tests
  - **Verified:** yes (2026-09-25)
- **AC4:** Given CI's install step, then pytest-xdist is installed before the suite step, so `test_lean_tmp_hygiene`'s `-n 2` variants run in CI rather than skip. Fails on: switching the runner without installing xdist (the variants skip, measured by BG0770)
  - **Verify:** pytest tools/tests/test_lean_one_runner.py::OneRunnerTests::test_ci_installs_xdist_before_the_suite
  - **Verified:** yes (2026-09-25)

## Notes

Merges QA's N6 and the engineering NEW-C. Direction: CI moves to the push's runner, not the push to CI's. That deletes a runner rather than adding a second run to a push already near the harness's 600s cap (unittest discover of tools/tests measured 212s serial), and it fixes BG0770's xdist skip in CI. QA's N6 AC2 as written (a leaked global the shared runner fails) holds only under unittest, so it is replaced by AC2 here: the same verdict from both, whichever it is. `test_lean_python_floor.SUITE_RUN` pins the CI command and changes with it. Out of scope, stated: the skill tree still runs under unittest in CI (`skill-tests.sh`), because the coverage gate and the test-noise gate read that run; its runner-only class is also caught at the tag by `module-alone`, and no skill-tree runner escape is recorded. Ratchet: no new check; one command replaced by another.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-25 | sdlc-studio v6 planning | Created for v6.0.0 Sprint 5 from the seat planning (NEW-C) |
