# US0121: G1 plan refuses an RFC or CR as a sprint unit and names the decompose command

> **Status:** Done
> **Created:** 2026-07-15
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py
> **Epic:** EP0033
> **Points:** 2

## User Story

**As an** operator planning a sprint
**I want** `sprint plan` to refuse an RFC or CR as a sprint unit and name the command that decomposes it
**So that** the Delivery backlog I plan is stories and bugs - work with executable ACs - never a request that has none.

## Acceptance Criteria

### AC1: plan refuses a request in the plannable set

- **Given** a worklist (or a `--crs`/`--rfcs` selection) that includes a CR or an RFC
- **When** `sprint plan` runs
- **Then** it refuses, names the request id(s), and points at the decomposition path (a request becomes work by being broken into stories/bugs); no plan is printed
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_two_backlogs.py::PlanRefusesRequestTests
- **Verified:** yes (2026-07-15)

### AC2: a pure product-backlog batch still plans

- **Given** a worklist of only stories and bugs, all groomed
- **When** `sprint plan` runs
- **Then** it plans normally - the refusal is specific to requests, not a regression of the planner
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_two_backlogs.py::PlanRefusesRequestTests
- **Verified:** yes (2026-07-15)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-15 | sdlc-studio | Created via `new` (deterministic) |
