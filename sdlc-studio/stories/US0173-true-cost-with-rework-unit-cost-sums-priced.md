# US0173: True cost with rework: unit cost sums priced tokens over every attempt, from an offline model price table

> **Status:** Done
> **Created:** 2026-07-16
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/telemetry.py
> **Epic:** EP0048
> **Points:** 3

## User Story

**As an** operator asking whether the cheap model was a false economy
**I want** true cost summed over attempts, priced offline
**So that** a cheap-first choice that escalated is not reported as cheap

## Acceptance Criteria

### AC1: cost sums priced tokens over every attempt; an unpriced model is named not guessed; config overrides the default

- **Given** an escalation record (haiku then opus), an unpriced-model record, and a pricing config override
- **When** `unit_cost` prices them
- **Then** cost sums over attempts, an unpriced model's tokens are counted but its dollars are not (named in `unpriced`), and a `pricing.<model>` config value overrides the estimate default
- **Verify:** shell python3 -m unittest discover -s .claude/skills/sdlc-studio/scripts/tests -p test_telemetry.py -k AttemptsAndCost
- **Verified:** yes (2026-07-16)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-16 | sdlc-studio | Created via `new` (deterministic) |
