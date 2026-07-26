# US0422: the stated strategy names the units worth mutating, replacing the blanket close-scoped sweep

> **Status:** Done
> **Delivers:** RFC0049
> **Created:** 2026-07-24
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/mutation.py, .claude/skills/sdlc-studio/scripts/gate.py, .claude/skills/sdlc-studio/scripts/tests/test_mutation.py
> **Epic:** EP0157
> **Points:** 3

## User Story

**As a** {{role}}
**I want** {{capability}}
**So that** {{benefit}}

## Acceptance Criteria

### AC1: the strategy names which units to mutate

- **Given** a batch whose stated strategy marks a subset of units as needing mutation evidence
- **When** the mutation run is scoped
- **Then** it mutates those units and reports the ones it did not, so the selection is a stated decision rather than a budget accident
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_mutation.py::StrategyScopedTests::test_the_run_mutates_the_units_the_strategy_named
- **Verified:** yes (2026-07-24)

### AC2: the blanket close-scoped sweep is replaced, not supplemented

- **Given** a close with a stated strategy present
- **When** the close runs
- **Then** the whole-sprint-diff sweep does not also run - two selection rules produce two answers about the same question, and the close currently spends its ceiling on whichever it reaches first
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_mutation.py::StrategyScopedTests::test_the_blanket_sweep_does_not_also_run
- **Verified:** yes (2026-07-24)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-24 | sdlc-studio | Created via `new` (deterministic) |
