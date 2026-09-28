# US0965: An eval scenario runs a two-unit lean sprint in a fresh project from plan to close, so v6's headline is measured, not asserted

> **Status:** In Progress
> **Created:** 2026-09-28
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** evals/scenarios/09-lean-sprint.json, tools/tests/test_eval_run.py, changelog.d/US0965.md
> **Epic:** EP0267
> **Points:** 3
> **Persona:** Maya Okafor

## User Story

**As a** maintainer deciding whether v6.0.0 ships
**I want** an eval in which a fresh agent runs a two-unit lean sprint from plan to close
**So that** the release claims only what a user can do from the shipped docs

## Acceptance Criteria

- **AC1:** Given evals/scenarios/09-lean-sprint.json, when `tools/eval_run.py setup --scenario 09-lean-sprint --dir <fresh dir>` runs, then it exits 0 and builds an initialised sdlc-studio project (config, indexes, a PRD, one epic) holding exactly two Ready stories of 1-2 points each, each with an executable `Verify:` line that fails on the fixture as built (nothing is implemented yet), and `validate.py check` passes on it. Fails on: a prose-only setup, a story already implemented, or a fixture the skill's own validator rejects
  - **Verify:** pytest tools/tests/test_eval_run.py::LeanSprintScenarioTests::test_the_fixture_builds_and_its_criteria_start_red
- **AC2:** Given the scenario, then its blocking behaviours grade the whole loop: `sprint plan` run with a forecast; each unit's Verify lines passing; each unit reviewed by a separate context briefed with `critic.py brief` and its verdict recorded with `critic.py record`; each story moved to Done by `transition.py`; `sprint close` run and its report produced; the worker stopping for the operator's signature rather than signing. Its forbidden behaviours include the worker signing the run, a hand-authored `_index.md` or id, and `--no-verify`. Fails on: a scenario that grades only artefacts and could pass a run that skipped review or signed itself
  - **Verify:** pytest tools/tests/test_eval_run.py::LeanSprintScenarioTests::test_the_scenario_grades_the_whole_loop
- **AC3:** Given the scenario run once by a fresh headless worker (allowed to spawn subagents) against the skill on main, graded by an independent grader through `tools/eval_run.py record`, then the result is recorded in the v6 eval run with each behaviour's evidence, and every blocking fail is filed as a bug before the cut. Fails on: an unrecorded run, or a blocking fail left unfiled
  - **Verify:** manual the orchestrator runs the scenario headless, an independent grader records each behaviour, and blocking fails are filed (D0280)

## Summary

v6's headline is the lean sprint loop, yet none of the eight eval scenarios runs a sprint. This sprint's orchestrator needed five scratch scripts to drive brief, review, record, land and transition, so whether a fresh agent in a consuming project can run the loop from the shipped docs alone is unproven. D0280 gates v6.0.0 on this scenario: pass and v6.0.0 ships as planned; fail and what it fails on is built before the cut.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-28 | sdlc-studio | Created via `new` (deterministic) |
