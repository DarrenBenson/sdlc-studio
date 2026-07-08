# US0085: Per-tier telemetry: tier fields and per-tier summary grouping

> **Status:** Done
> **Created:** 2026-07-08
> **Created-by:** sdlc-studio new
> **Epic:** EP0008
> **Persona:** Sam Eriksson (QA)
> **CR:** CR-0191 (RFC-0026 WS3)
> **Depends on:** US0083

## User Story

**As an** operator calibrating the routing policy
**I want** telemetry to record which tier was recommended vs delivered per unit, and summaries grouped per delivered tier
**So that** per-tier escape and escalation rates are measurable instead of asserted

## Acceptance Criteria

### AC1: Tier fields recorded

- **Given** a unit closed after a routed delivery
- **When** `telemetry record --tier-recommended small --tier-delivered medium --model <id> --escalated true` runs
- **Then** the record carries the four new fields; absent fields stay omitted (whitelist discipline unchanged)
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_telemetry.py -k tier_fields
- **Verified:** yes (2026-07-08)

### AC2: Summary groups per delivered tier

- **Given** a log with records across two delivered tiers
- **When** `telemetry show --summary` runs
- **Then** critic-verdict mix and reopen rate are additionally reported per tier_delivered; with no tier-carrying records, no per-tier block appears
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_telemetry.py -k per_tier
- **Verified:** yes (2026-07-08)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-08 | sprint: CR0191 | Created via `new` (deterministic) |
