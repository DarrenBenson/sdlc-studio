# US0979: A lane brief and return open and close the unit's span

> **Status:** Ready
> **Delivers:** CR0605
> **Created:** 2026-10-02
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_lean_lane_unit_span.py, changelog.d/CR0605.md
> **Epic:** EP0271
> **Points:** 3
> **Persona:** Maya Okafor

## User Story

**As a** Maya Okafor
**I want** A lane brief and return open and close the unit's span
**So that** CR0605 is delivered by work that can be planned and checked

## Acceptance Criteria

### AC1: A lane brief and return measure the unit

- **Given** a unit X in the open run's batch with no In Progress span
- **When** `sprint lane brief --units X` is issued and later `sprint lane return --units X` passes
- **Then** X's span opens at the brief and closes at the return, the page reports X's minutes measured over that span, and no new flag or refusal is added. Fails on: the current code opens no span, so X reads NOT MEASURED
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_lane_unit_span.py::LaneUnitSpanTests::test_a_lane_brief_and_return_measure_the_unit

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-02 | sdlc-studio | Created via `new` (deterministic) |
| 2026-10-02 | engineering seat (orchestrator) | Groomed from the request's criterion; premise: RPT0014 reads NOT MEASURED / 0.2x |
