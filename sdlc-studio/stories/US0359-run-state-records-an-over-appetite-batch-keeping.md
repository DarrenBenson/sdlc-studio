# US0359: run_state records an over-appetite batch, keeping both the standing and the accepted appetite

> **Status:** Draft
> **Delivers:** CR0349
> **Created:** 2026-07-23
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Epic:** EP0124
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/lib/run_state.py, .claude/skills/sdlc-studio/scripts/tests/test_run_state.py

## User Story

**As a** {{role}}
**I want** {{capability}}
**So that** {{benefit}}

## Acceptance Criteria

### AC1: run_state keeps BOTH the standing appetite and the accepted one

- **Given** a batch of 32 units planned against a standing appetite of 8
- **When** the plan is written with `--appetite-units 32`
- **Then** run_state records both numbers - the standing appetite and the one accepted for this run - so the over-commitment survives the decision to accept it
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_run_state.py::OverAppetiteTests::test_both_the_standing_and_accepted_appetite_are_recorded

### AC2: raising the ceiling does not erase the overage

- **Given** the same run
- **When** the recorded plan is read back
- **Then** it reports 32 against a standing 8, not 32/32 - the record must not say the batch fitted when it was made to fit
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_run_state.py::OverAppetiteTests::test_the_plan_does_not_read_as_fitting

### AC3: a run within appetite records no overage

- **Given** a batch inside the standing appetite
- **When** the plan is written
- **Then** no over-commitment is recorded - the field must distinguish an accepted overage from an ordinary run, or it means nothing
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_run_state.py::OverAppetiteTests::test_a_within_appetite_run_records_no_overage

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-23 | sdlc-studio | Created via `new` (deterministic) |
