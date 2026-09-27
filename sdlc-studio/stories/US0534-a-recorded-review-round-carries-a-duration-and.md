# US0534: A recorded review round carries a duration, and a round recorded without one says so rather than counting as zero

> **Status:** Done
> **Delivers:** CR0466
> **Created:** 2026-07-28
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/critic.py, .claude/skills/sdlc-studio/scripts/tests/test_critic.py
> **Epic:** EP0182
> **Points:** 3
> **Persona:** Maya Okafor

## User Story

**As a** an operator reading what a sprint cost
**I want** a recorded review round to carry its duration, and an untimed one to say so
**So that** review time is a measured number rather than a silence counted as zero

## Acceptance Criteria

### AC1: a review round carries a duration

- **Given** a review round recorded with a start and an end
- **When** the round is written to the review record
- **Then** the round carries its duration
- **Verify:** manual - retired by BG0783: `record_review_round`, the only writer of a round duration, had no caller after US0918 and is deleted with its ledger
- **Verified:** manual (2026-09-27) - retired, superseded by BG0783

### AC2: a round with no duration says so rather than counting as zero

- **Given** a review round recorded without timing information
- **When** the round is read back
- **Then** its duration reads as unmeasured, and nothing treats it as zero elapsed
- **Verify:** manual - retired by BG0783: `record_review_round`, the only writer of a round duration, had no caller after US0918 and is deleted with its ledger
- **Verified:** manual (2026-09-27) - retired, superseded by BG0783

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-28 | sdlc-studio | Created via `new` (deterministic) |
| 2026-07-28 | Claude Opus 5 | Groomed: criteria authored against this story's slice, each with an executable Verify line |
| 2026-09-27 | BG0783 | AC1 and AC2 retired in the D0259 pattern: `record_review_round`, the only writer of a round duration, had no caller after US0918 and is deleted with its ledger |
