# US1263: CI runs the skill suite through the push gate's own pytest plan, under coverage, so a test green at push is green in CI

> **Status:** Draft
> **Risk-class:** standard
> **Delivers:** CR0712
> **Created:** 2026-11-17
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .github/workflows/lint.yml, tools/skill-tests.sh, tools/tests/test_lean_one_runner.py
> **Epic:** EP0352
> **Points:** 5
> **Persona:** Rowan Achterberg

## User Story

**As a** Rowan Achterberg
**I want** CI runs the skill suite through the push gate's own pytest plan, under coverage, so a test green at push is green in CI
**So that** CR0712 is delivered by work that can be planned and checked

## Acceptance Criteria

### AC1: CI runs the skill suite through the push's plan

- **Given** `.github/workflows/lint.yml` and `tools/skill-tests.sh` as shipped
- **When** the workflow's suite step and the script's full-suite path are read
- **Then** the command CI runs over the skill test directory is the push boundary's own pytest plan (`gate.py --boundary push --run-tests`), and no workflow step runs the whole skill suite under `unittest discover`. Fails on: HEAD, where CI runs `skill-tests.sh` and that runs `python3 -m unittest discover` while the push runs pytest
- **Verify:** pytest tools/tests/test_lean_one_runner.py::SkillSuiteOneRunnerTests::test_ci_runs_the_skill_suite_through_the_push_plan

### AC2: CI and the push give the same verdict on a module the two runners split

- **Given** a fixture project whose skill test directory holds a pair of modules green under the push's pytest plan and red under `unittest discover` (the shape of the hits on US0977 and BG1489)
- **When** CI's command, read from lint.yml, and the push's full-suite lane are each run over it
- **Then** both return the same verdict, and a control shows the pair still splits `unittest discover` from the push, so the agreement is the runner and not a pair that never fails. Fails on: a test green at the push and red in CI for the runner alone
- **Verify:** pytest tools/tests/test_lean_one_runner.py::SkillSuiteOneRunnerTests::test_ci_and_push_agree_on_a_skill_module_the_runners_split

### AC3: The one run is measured under coverage

- **Given** the CI suite command run over a fixture skill directory with coverage switched on as lint.yml switches it on
- **When** the run finishes and `coverage report` is read
- **Then** the report holds line data for the fixture's script, including lines reached only in a worker process, and the suite ran once. Fails on: a coverage gate reading an empty or main-process-only data file, or the suite run a second time to collect coverage
- **Verify:** pytest tools/tests/test_lean_one_runner.py::SkillSuiteOneRunnerTests::test_the_push_plan_run_writes_coverage_from_one_run

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-17 | sdlc-studio | Created via `new` (deterministic) |
