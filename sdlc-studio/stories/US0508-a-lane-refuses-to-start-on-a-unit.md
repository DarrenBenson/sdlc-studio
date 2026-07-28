# US0508: A lane refuses to start on a unit that carries no acceptance criteria, naming it rather than inferring a contract

> **Status:** Review
> **Delivers:** CR0463
> **Created:** 2026-07-28
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py
> **Epic:** EP0178
> **Points:** 3
> **Persona:** Maya Okafor

## User Story

**As a** lane picking up a unit with nothing to deliver against
**I want** the lane to refuse a unit carrying no acceptance criteria rather than inferring a contract from its summary
**So that** six units cannot reach Fixed with no criterion again, as they did in the last sprint

## Acceptance Criteria

### AC1: a unit with no acceptance-criteria section is refused at dispatch

- **Given** a unit whose artefact carries no acceptance-criteria section
- **When** a lane is dispatched onto it
- **Then** it refuses, naming the unit and what is missing, rather than inferring the contract from the summary
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::LaneContractTests::test_a_unit_with_no_criteria_is_refused_at_dispatch

### AC2: a unit whose criteria are an ungroomed placeholder is refused the same way

- **Given** a unit whose criteria section is the scaffold marker rather than authored content
- **When** a lane is dispatched
- **Then** it refuses, because a placeholder is an absent contract wearing the shape of one
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::LaneContractTests::test_an_ungroomed_placeholder_is_refused_too

### AC3: the mechanism is reached by a named caller

- **Given** the mechanism this unit adds
- **When** the caller check runs over this unit
- **Then** the consuming call site is named and resolves in the tree, so the mechanism is
  reachable in production rather than correct in isolation
- **Caller:** `sprint lane brief` (cmd_lane -> lane_dispatch -> lane_contract), documented in help/sprint.md
- **Verify:** shell python3 .claude/skills/sdlc-studio/scripts/critic.py caller-check --unit US0508 --root .

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-28 | sdlc-studio | Created via `new` (deterministic) |
| 2026-07-28 | Claude Fable 5 | Groomed against the carried lessons |
| 2026-07-28 | Claude Fable 5 | Caller named at review - this unit's own check reported it caller-unnamed |
