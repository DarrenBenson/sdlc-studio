# US0580: Only REGRESSION and NEW hold a gate: a PRE-EXISTING finding is reported and does not block

> **Status:** Draft
> **Delivers:** CR0512
> **Created:** 2026-08-01
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/critic.py, .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py
> **Epic:** EP0194
> **Points:** 5
> **Persona:** Maya Okafor

## User Story

**As a** {{role}}
**I want** {{capability}}
**So that** {{benefit}}

## Acceptance Criteria

### AC1: a pre-existing finding does not hold the gate

- **Given** a recorded verdict whose only findings are classified PRE-EXISTING
- **When** the coverage gate reads it
- **Then** the unit is covered and the findings are reported with their classification, because anything already true of the tree is not this unit's debt
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::BlockingScopeTests::test_a_pre_existing_finding_does_not_block

### AC2: a regression still blocks

- **Given** a verdict carrying one REGRESSION finding
- **When** the coverage gate reads it
- **Then** the unit is NOT covered - the positive control, so the change cannot be satisfied by a gate that stopped blocking
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::BlockingScopeTests::test_a_regression_still_blocks

### AC3: the blocking set is reported separately from the rest

- **Given** a verdict mixing REGRESSION, NEW and PRE-EXISTING findings
- **When** the verdict is rendered
- **Then** the blocking set names only the first two, and the non-blocking set names the third with its reason, so a reader can tell what held the gate from what was merely noticed
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::BlockingScopeTests::test_the_two_sets_are_reported_apart

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-01 | sdlc-studio | Created via `new` (deterministic) |
