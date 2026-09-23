# US0871: Each unit's elapsed time and tokens are measured as it is delivered

> **Status:** In Progress
> **Created:** 2026-09-23
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/transition.py, .claude/skills/sdlc-studio/scripts/lib/run_state.py, .claude/skills/sdlc-studio/scripts/tests/test_lean_unit_actuals.py
> **Epic:** EP0260
> **Points:** 5
> **Persona:** Maya Okafor

## User Story

**As a** operator judging estimate accuracy
**I want** each unit's elapsed time and tokens measured as it is delivered
**So that** time and token accuracy can be reported per unit rather than guessed from the run's span

## Acceptance Criteria

- **AC1:** Given an open run, when a batch unit moves to In Progress, then run state key `unit_actuals` records its start time and the run's token total at that moment
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_unit_actuals.py::UnitActualsTests::test_starting_a_unit_stamps_its_time_and_tokens
- **AC2:** Given a started unit, when it reaches a terminal status, then `unit_actuals` records its elapsed minutes and token delta, and a unit that re-enters In Progress accumulates rather than restarts
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_unit_actuals.py::UnitActualsTests::test_finishing_a_unit_records_minutes_and_tokens
- **AC3:** Given a unit transitioned when no run is open, or one outside the batch, when it moves, then nothing is recorded and the transition is unaffected
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_unit_actuals.py::UnitActualsTests::test_a_unit_outside_a_run_records_nothing
- **AC4:** Given the token meter cannot be read, when a unit finishes, then its tokens read not measured, never 0
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_unit_actuals.py::UnitActualsTests::test_an_unreadable_meter_is_not_measured

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-23 | sdlc-studio | Created via `new` (deterministic) |
