# US1274: The TSD names the eval step in its release stage and its coverage row matches the scenarios on disk

> **Status:** Draft
> **Risk-class:** standard
> **Delivers:** CR0718
> **Created:** 2026-11-17
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** sdlc-studio/tsd.md, tools/tests/test_lean_tsd_refresh.py
> **Epic:** EP0357
> **Points:** 2
> **Persona:** Abena Osei

## User Story

**As a** Abena Osei
**I want** The TSD names the eval step in its release stage and its coverage row matches the scenarios on disk
**So that** CR0718 is delivered by work that can be planned and checked

## Acceptance Criteria

### AC1: The release stage names the eval step and where its result is kept

- **Given** `sdlc-studio/tsd.md`
- **When** its Before a release tag stage and each section that calls the eval scenarios a gate (In Scope, Test Strategy item 4, the Coverage Targets row and the Eval Scenarios section) are read
- **Then** the release stage names `eval_run.py report --run <version>` as a step and `evals/.results/` as where its result is committed, and every section that calls the scenarios a gate says the gate is that release step run by hand, none claiming a hook, a workflow or `gate.py` runs it. Fails on: the TSD as it stands at grooming, whose release stage lists no eval step while four sections present the level as gated
- **Verify:** pytest tools/tests/test_lean_tsd_refresh.py::EvalStepTests::test_the_release_stage_names_the_eval_step_and_its_result

### AC2: The coverage row names the scenarios on disk

- **Given** the scenario files under `evals/scenarios/` and the TSD's Coverage Targets row for eval scenarios
- **When** the row is compared with the directory
- **Then** the row names every scenario on disk by its id and names none that is absent. Fails on: a scenario file added or removed with the row unchanged, as at grooming, where the row speaks of four surfaces and nine scenarios exist
- **Verify:** pytest tools/tests/test_lean_tsd_refresh.py::EvalStepTests::test_the_coverage_row_names_every_scenario_on_disk

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-17 | sdlc-studio | Created via `new` (deterministic) |
