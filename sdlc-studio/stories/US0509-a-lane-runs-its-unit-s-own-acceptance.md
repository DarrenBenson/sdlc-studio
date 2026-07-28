# US0509: A lane runs its unit's own acceptance criteria before returning, and a unit whose criteria do not pass comes back blocked

> **Status:** Review
> **Delivers:** CR0463
> **Created:** 2026-07-28
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py
> **Epic:** EP0178
> **Points:** 5
> **Persona:** Maya Okafor

## User Story

**As a** reviewer whose time is spent on defects a lane could have caught
**I want** each lane to run its unit's own acceptance criteria before returning
**So that** a unit arrives at review with its basic criteria already proven, leaving review for the judgement only a reader can supply

## Acceptance Criteria

### AC1: a unit whose criteria do not pass comes back blocked, not fixed

- **Given** a lane that has finished editing and whose unit has a red executable criterion
- **When** the lane returns
- **Then** the unit is reported blocked with the failing criterion named, never as fixed
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::LaneVerifyTests::test_a_red_criterion_returns_blocked_not_fixed

### AC2: the result carries the verification output, not a claim about it

- **Given** a lane returning a unit
- **When** the result is read
- **Then** it carries the verifier's own output for each criterion, so the claim can be checked rather than trusted
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::LaneVerifyTests::test_the_result_carries_the_verifier_output

### AC3: a criterion the runner cannot resolve is reported unresolved, never as passing

- **Given** a criterion whose selector names a test that does not exist
- **When** the lane verifies
- **Then** it reports the criterion unresolved and the unit blocked - an unanswerable check is not a passed one
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::LaneVerifyTests::test_an_unresolvable_criterion_is_not_a_pass

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-28 | sdlc-studio | Created via `new` (deterministic) |
| 2026-07-28 | Claude Fable 5 | Groomed against the carried lessons |
