# US0236: sprint close --apply-signoff records per-unit sign-off and Done transitions, refusing without an explicit principal

> **Status:** Draft
> **Created:** 2026-07-17
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/critic.py, .claude/skills/sdlc-studio/scripts/transition.py
> **Epic:** EP0077
> **Points:** 5

## User Story

**As a** {{role}}
**I want** {{capability}}
**So that** {{benefit}}

## Acceptance Criteria

> Seeded from the request's full criteria list - redistribute across this epic's stories as you groom them.

### AC1: One command fans a recorded operator approval into per-unit sign-offs, Done transitions, telemetry

- **Given** {{context}}
- **When** {{action}}
- **Then** One command fans a recorded operator approval into per-unit sign-offs, Done transitions, telemetry closes, parent derivations and the velocity row, stopping loudly at the first refusal
- **Verify:** {{executable check}}

### AC2: It never runs without an explicit principal; authoring-session subagents are refused as principals

- **Given** {{context}}
- **When** {{action}}
- **Then** It never runs without an explicit principal; authoring-session subagents are refused as principals exactly as critic signoff refuses them
- **Verify:** {{executable check}}

### AC3: Re-running after a mid-cascade stop is idempotent

- **Given** {{context}}
- **When** {{action}}
- **Then** Re-running after a mid-cascade stop is idempotent
- **Verify:** {{executable check}}

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-17 | sdlc-studio | Created via `new` (deterministic) |
