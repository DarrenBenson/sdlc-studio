# US0126: G1 plan-refusal fires only when enforced

> **Status:** Done
> **Created:** 2026-07-15
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py
> **Epic:** EP0034
> **Points:** 2

## User Story

**As an** operator on a project that has not opted into the two-backlog workflow
**I want** `sprint plan` to keep planning a CR as before
**So that** upgrading the skill does not break my existing sprint flow until I opt in.

## Acceptance Criteria

### AC1: the G1 request-refusal is gated on enforcement

- **Given** an enforced project and an unenforced one, each with a CR batch
- **When** `sprint plan --crs` runs
- **Then** the enforced project refuses the CR as a request (naming the decompose path); the unenforced project plans it as before (no request refusal)
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_two_backlogs.py::PlanRefusesRequestTests
- **Verified:** yes (2026-07-15)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-15 | sdlc-studio | Created via `new` (deterministic) |
