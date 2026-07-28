# US0534: A recorded review round carries a duration, and a round recorded without one says so rather than counting as zero

> **Status:** Draft
> **Delivers:** CR0466
> **Created:** 2026-07-28
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/critic.py
> **Epic:** EP0182
> **Points:** 3
> **Persona:** Maya Okafor

## User Story

**As a** {{role}}
**I want** {{capability}}
**So that** {{benefit}}

## Acceptance Criteria

### AC1: a review round carries a duration

- **Given** a review round recorded with a start and an end
- **When** the round is written to the review record
- **Then** the round carries its duration
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic.py::ReviewDurationTests::test_a_recorded_round_carries_its_duration

### AC2: a round with no duration says so rather than counting as zero

- **Given** a review round recorded without timing information
- **When** the round is read back
- **Then** its duration reads as unmeasured, and nothing treats it as zero elapsed
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic.py::ReviewDurationTests::test_an_untimed_round_reads_unmeasured_not_zero

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-28 | sdlc-studio | Created via `new` (deterministic) |
| 2026-07-28 | Claude Opus 5 | Groomed: criteria authored against this story's slice, each with an executable Verify line |
