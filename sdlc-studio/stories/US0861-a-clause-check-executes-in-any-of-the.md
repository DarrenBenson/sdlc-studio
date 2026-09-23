# US0861: a clause check executes in any of the three ruled shapes, and a check that cannot be run reports `unknown` rather than green

> **Status:** Superseded
> **Delivers:** RFC0060
> **Created:** 2026-09-21
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/verify_ac.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py
> **Epic:** EP0258
> **Points:** 8
> **Persona:** Maya Okafor

## User Story

**As a** Maya Okafor
**I want** a clause check executes in any of the three ruled shapes, and a check that cannot be run reports `unknown` rather than green
**So that** RFC0060 is delivered by work that can be planned and checked

## Acceptance Criteria

- [ ] **AC1: a selector-shaped check runs through the existing verifier.**
  - **Given** a clause whose check is a `pytest ...` selector
  - **When** the clause is evaluated
  - **Then** its verdict is that selector's result, obtained through `verify_ac`'s own runner rather than a second implementation of it
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::ClauseCheckExecutionTests::test_a_selector_check_runs_through_the_shipped_verifier
- [ ] **AC2: a tool-verdict check compares a command's output to the expected verdict.**
  - **Given** a clause whose check names a command and the verdict it must produce
  - **When** the clause is evaluated
  - **Then** it is green only when the command produced that verdict - this is the shape RUN-01M306PY's second clause needed and did not have
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::ClauseCheckExecutionTests::test_a_tool_verdict_check_compares_against_the_expected_verdict
- [ ] **AC3: a persona-judged check is refused unless it names its falsifier.**
  - **Given** a clause whose check is a persona-judged predicate with no `Falsifier:` field
  - **When** the clause is authored
  - **Then** it is refused - D0230's guard, and the whole reason the third shape was allowed at all
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::ClauseCheckExecutionTests::test_a_persona_check_without_a_falsifier_is_refused
- [ ] **AC4: a check that cannot be RUN reports `unknown`, never green.**
  - **Given** a clause whose check names a selector that does not resolve, or a command not on this machine
  - **When** the clause is evaluated
  - **Then** its verdict is `unknown` and the reason is recorded - a check that silently passes when it cannot run is worse than no check
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::ClauseCheckExecutionTests::test_an_unrunnable_check_is_unknown_not_green
- [ ] **AC5: a failing check is red, not unknown.**
  - **Given** a clause whose check runs to completion and fails
  - **When** it is evaluated
  - **Then** its verdict is `failed` - the discriminating half, because collapsing failed into unknown would make every miss look like a measurement gap
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::ClauseCheckExecutionTests::test_a_check_that_runs_and_fails_is_red_not_unknown
- [ ] **AC6: evaluation is reachable from the shipped command.**
  - **Given** a run whose plan carries clauses
  - **When** the close is invoked through the CLI
  - **Then** the clause results are present in run state - the wiring is the half a library test cannot see, and this project has shipped a correct library behind a dead entry point before
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::ClauseCheckExecutionTests::test_the_shipped_close_evaluates_the_clauses

## Test Plan

| Criterion | Mutant - the production change this test must fail on | Title |
| --- | --- | --- |
| AC1 | in `sprint.py`, evaluate a selector check with a fresh subprocess call rather than through `verify_ac`'s runner, losing its refusals | a selector check runs through the verifier |
| AC2 | in `sprint.py`, treat a tool-verdict check as green whenever the command exits 0, without comparing the verdict | a tool verdict is compared |
| AC3 | in `sprint.py`, accept a persona-judged clause that names no falsifier | a persona check needs a falsifier |
| AC4 | in `sprint.py`, map an unrunnable check to green instead of `unknown` | an unrunnable check is unknown |
| AC5 | in `sprint.py`, map a failing check to `unknown` alongside the unrunnable case | a failing check is red |
| AC6 | in `sprint.py`, leave clause evaluation unreachable from the close command, exercised only in-process | the shipped close evaluates clauses |

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-21 | sdlc-studio | Created via `new` (deterministic) |
