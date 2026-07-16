# US0172: Per-attempt telemetry: records carry an attempts list of model and tokens, a legacy record reads as one attempt

> **Status:** Done
> **Created:** 2026-07-16
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/telemetry.py
> **Epic:** EP0048
> **Points:** 5

## User Story

**As an** estimator that must stay falsifiable
**I want** telemetry to record model and tokens per attempt
**So that** an escalation shows its true summed cost instead of one flattering line

## Acceptance Criteria

### AC1: a record carries an attempts list; a legacy record reads as one attempt; nothing measured yields no fabricated attempt

- **Given** records with an attempts list, with only flat model/tokens, and with neither
- **When** `attempts_of` reads them
- **Then** the list is preserved in order, the legacy record reads as a single attempt, and a record with no measurement yields an empty list (no invented attempt)
- **Verify:** shell python3 -m unittest discover -s .claude/skills/sdlc-studio/scripts/tests -p test_telemetry.py -k AttemptsAndCost
- **Verified:** yes (2026-07-16)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-16 | sdlc-studio | Created via `new` (deterministic) |
