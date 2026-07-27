# US0498: The test strategy is persisted with the plan and read back at close, so it can be reviewed, signed off and compared with what ran

> **Status:** Ready
> **Delivers:** CR0453
> **Created:** 2026-07-28
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py
> **Epic:** EP0177
> **Points:** 5
> **Persona:** Maya Okafor

## User Story

**As a** reviewer asked to sign off a plan
**I want** the test strategy persisted with the plan rather than printed and lost
**So that** it can be reviewed at plan time, signed off with the goal, and compared afterwards with what actually ran

## Acceptance Criteria

### AC1: the strategy is written into the plan record

- **Given** a planned batch
- **When** the plan is written
- **Then** the plan record carries the strategy, so it survives the terminal and can be read back
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::TestStrategyPersistenceTests::test_the_strategy_is_persisted_with_the_plan

### AC2: the close reads it back

- **Given** a closed run whose plan carried a strategy
- **When** the close runs
- **Then** it reads the recorded strategy rather than re-deriving one, so what is judged at close is what was agreed at plan
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::TestStrategyPersistenceTests::test_the_close_reads_back_the_recorded_strategy

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-28 | sdlc-studio | Created via `new` (deterministic) |
| 2026-07-28 | Claude Fable 5 | Groomed |
