# US0513: A unit whose mechanism has no caller yet says so explicitly and names the follow-up that completes it

> **Status:** Review
> **Delivers:** CR0461
> **Created:** 2026-07-28
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/validate.py, .claude/skills/sdlc-studio/scripts/tests/test_validate.py
> **Epic:** EP0178
> **Points:** 3
> **Persona:** Maya Okafor

## User Story

**As a** reader of a unit that ships half a capability
**I want** a unit whose mechanism has no caller yet to say so explicitly and name the follow-up
**So that** a consumer with no producer is recorded as such rather than reading as complete

## Acceptance Criteria

### AC1: a unit declaring itself consumer-only or producer-only passes the caller check

- **Given** a unit that states its scope as one half of a capability and names the follow-up unit
- **When** the check runs
- **Then** it passes, because the gap is recorded rather than implied
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_validate.py::PartialCapabilityTests::test_a_declared_partial_capability_is_accepted
- **Verified:** yes (2026-07-28)

### AC2: a declaration naming no follow-up is refused

- **Given** a unit declaring itself consumer-only with no follow-up named
- **When** the check runs
- **Then** it is refused, since an acknowledged gap nobody owns is the same as an unacknowledged one
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_validate.py::PartialCapabilityTests::test_a_partial_capability_must_name_its_follow_up
- **Verified:** yes (2026-07-28)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-28 | sdlc-studio | Created via `new` (deterministic) |
| 2026-07-28 | Claude Fable 5 | Groomed against the carried lessons |
