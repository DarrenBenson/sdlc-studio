# US0626: sprint close and sprint stop refuse while any batch unit is non-terminal, naming each and where its findings went

> **Status:** Ready
> **Delivers:** CR0526
> **Created:** 2026-08-02
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py
> **Epic:** EP0206
> **Points:** 5
> **Persona:** Maya Okafor

## User Story

**As a** operator closing a sprint
**I want** `sprint close` and `sprint stop` to refuse while any batch unit is non-terminal, naming each unit and where its findings went
**So that** a run cannot be recorded as finished over work that never reached a terminal status

## Acceptance Criteria

### AC1: close refuses while a batch unit is non-terminal

- **Given** an open run whose batch holds a unit at a pre-terminal status
- **When** `sprint.py close` runs
- **Then** it refuses and NAMES that unit and its status - a close over unfinished work records a run that did not happen
- **Mutant:** report the non-terminal unit as an advisory - the close completes and the record claims work that is not done
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::CloseRefusesNonTerminalTests::test_close_refuses_and_names_the_unit

### AC2: stop refuses on the same condition

- **Given** the same run
- **When** `sprint.py stop` runs instead
- **Then** it refuses on the same condition, because abandoning a run and closing one both write a record a later reader trusts
- **Mutant:** leave `stop` ungated - the same unfinished batch is recorded through the other verb
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::CloseRefusesNonTerminalTests::test_stop_refuses_on_the_same_condition

### AC3: the refusal says where the unit's findings went

- **Given** a non-terminal unit carrying recorded findings
- **When** either verb refuses
- **Then** the refusal names the artefact the findings were filed to, so the operator can judge whether the unit is genuinely unfinished or merely unrecorded
- **Mutant:** print the unit id alone - the operator is told something is wrong and not what to read
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::CloseRefusesNonTerminalTests::test_the_refusal_names_where_the_findings_went

### AC4: a fully terminal batch still closes

- **Given** a run whose every batch unit is terminal
- **When** `sprint.py close` runs
- **Then** it proceeds - a gate that refuses every close is not a gate
- **Mutant:** refuse unconditionally - the control that proves this discriminates
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::CloseRefusesNonTerminalTests::test_a_terminal_batch_still_closes

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-02 | sdlc-studio | Created via `new` (deterministic) |
