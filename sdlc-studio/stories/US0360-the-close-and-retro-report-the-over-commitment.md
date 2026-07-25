# US0360: the close and retro report the over-commitment, not the raised ceiling

> **Status:** Review
> **Delivers:** CR0349
> **Created:** 2026-07-23
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Epic:** EP0124
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/retro.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py

## User Story

**As a** reader of a close or retro for an over-appetite run
**I want** the over-commitment reported, not the raised ceiling
**So that** I can find why the run overran, and see the decision to accept it rather than a batch that looks like it fitted

## Acceptance Criteria

### AC1: the close reports the over-commitment

- **Given** a run recorded as over-appetite
- **When** `sprint close` runs
- **Then** its output states the batch was N units against a standing appetite of M, rather than reporting the raised ceiling as though it were the plan
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::OverAppetiteReportTests::test_the_close_states_the_overage_not_the_raised_ceiling
- **Verified:** yes (2026-07-25)

### AC2: the retro carries the overage so a later reader can find it

- **Given** the same run's retro
- **When** it is generated
- **Then** it records the over-commitment and the decision to accept it - a retro asking why a run overran must find the trace, which is exactly what CR0349 reported missing
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_retro.py::OverAppetiteReportTests::test_the_retro_records_the_overage_and_its_acceptance
- **Verified:** yes (2026-07-25)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-23 | sdlc-studio | Created via `new` (deterministic) |
