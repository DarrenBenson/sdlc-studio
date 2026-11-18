# US1238: A red CI run is recorded against its filed flaky bug and rerun once, or filed as a regression holding pushes

> **Status:** Draft
> **Risk-class:** high
> **Delivers:** CR0697
> **Created:** 2026-11-17
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/gate.py, .claude/skills/sdlc-studio/help/gate.md, .claude/skills/sdlc-studio/reference-test-validation.md, .claude/skills/sdlc-studio/scripts/tests/test_ci_red_run_policy.py
> **Epic:** EP0340
> **Points:** 5
> **Persona:** Abena Osei

## User Story

**As a** Abena Osei
**I want** A red CI run is recorded against its filed flaky bug and rerun once, or filed as a regression holding pushes
**So that** CR0697 is delivered by work that can be planned and checked

## Acceptance Criteria

### AC1: A red run on a filed flaky test is recorded against its bug and rerun once

- **Given** a red CI run whose one failing test is named by an open bug filed as flaky, a token that may rerun jobs, and the default rerun limit
- **When** the red run is put through the red-run command of `gate.py`
- **Then** the run is recorded on that bug, the answer is to rerun the failed jobs once, and a second red of the same run answers stop, with the limit reached. Fails on: a rerun with nothing recorded on the bug, a second rerun past the limit, or any answer that skips or deselects the test
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_ci_red_run_policy.py::CiRedRunPolicyTests::test_a_filed_flake_is_recorded_on_its_bug_and_rerun_once

### AC2: Without a token that can rerun, the agent stops and asks the operator

- **Given** the same red run and a token that cannot rerun jobs
- **When** the red run is put through the command
- **Then** the run is still recorded on the bug, and the answer is to stop and ask the operator to rerun, naming the run and the bug. Fails on: a rerun attempted and its failure read as a second red, or a silent stop that names no one to act
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_ci_red_run_policy.py::CiRedRunPolicyTests::test_a_token_that_cannot_rerun_stops_and_asks_the_operator

### AC3: A red run matching no filed flake is a regression that holds pushes

- **Given** a red run with one failing test no open flaky bug names, and a second run with two failing tests of which only one is a filed flake
- **When** each is put through the command
- **Then** each is answered as a regression: a bug is filed through the shipped filer naming the run and the failing test, no rerun is offered, and the answer says not to push again until main is green. Fails on: a run rerun as a flake because one of its failures is known, or a regression with no bug filed
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_ci_red_run_policy.py::CiRedRunPolicyTests::test_a_red_run_matching_no_filed_flake_is_a_regression

### AC4: The gate help and the test reference state the policy

- **Given** `help/gate.md` and the flakiness section of `reference-test-validation.md`
- **When** each is read for the red-run policy
- **Then** the help names the command and its three answers (rerun once, stop and ask the operator, regression), and the reference says a known flake is recorded and rerun within the configured limit and never skipped. Fails on: a reference that still offers only prevention advice, or help that names no command
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_ci_red_run_policy.py::CiRedRunPolicyTests::test_the_help_and_the_reference_state_the_red_run_policy

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-17 | sdlc-studio | Created via `new` (deterministic) |
