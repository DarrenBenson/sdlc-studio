# US0510: A lane returns the proof the test strategy assigned to its unit, or states plainly that it could not and why

> **Status:** Done
> **Delivers:** CR0463
> **Created:** 2026-07-28
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py
> **Epic:** EP0178
> **Points:** 3
> **Persona:** Maya Okafor

## User Story

**As a** operator reading a close that says the proof obligations were met
**I want** each lane to return the proof its unit was assigned, or to say why it could not
**So that** an obligation the plan declared cannot go unmet in silence, as six did last sprint

## Acceptance Criteria

### AC1: a lane returns the proof its unit was assigned

- **Given** a plan assigning a unit mutation proof beyond its unit tests
- **When** the lane returns that unit
- **Then** the result carries the assigned proof, identified by the obligation it discharges
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::LaneProofTests::test_a_lane_returns_the_assigned_proof

### AC2: an obligation it could not discharge is stated, not omitted

- **Given** a lane that could not run the assigned proof
- **When** it returns
- **Then** the result names the obligation and why it was not discharged, so the gap is visible at the lane rather than at the close
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::LaneProofTests::test_an_undischarged_obligation_is_stated_not_omitted

### AC3: the mechanism is reached by a named caller

- **Given** the mechanism this unit adds
- **When** the caller check runs over this unit
- **Then** the consuming call site is named and resolves in the tree, so the mechanism is
  reachable in production rather than correct in isolation
- **Caller:** `sprint lane brief` and `sprint lane return` (both call lane_proof), documented in help/sprint.md
- **Verify:** shell python3 .claude/skills/sdlc-studio/scripts/critic.py caller-check --unit US0510 --root .

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-28 | sdlc-studio | Created via `new` (deterministic) |
| 2026-07-28 | Claude Fable 5 | Groomed against the carried lessons |
| 2026-07-28 | Claude Fable 5 | Caller named at review - this unit's own check reported it caller-unnamed |
