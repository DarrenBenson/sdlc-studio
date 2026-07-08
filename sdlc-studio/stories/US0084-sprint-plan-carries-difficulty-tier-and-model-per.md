# US0084: Sprint plan carries difficulty, tier and model per unit

> **Status:** Done
> **Created:** 2026-07-08
> **Created-by:** sdlc-studio new
> **Epic:** EP0008
> **Persona:** Dani Okafor (Engineering)
> **CR:** CR-0190 (RFC-0026 WS2)
> **Depends on:** US0083

## User Story

**As an** orchestrator consuming the sprint plan
**I want** every planned unit to carry its difficulty (and, when routing is enabled, a tier and model recommendation)
**So that** worker spawning can honour the routing recommendation without a second analysis pass

## Acceptance Criteria

### AC1: Difficulty emitted under both orders

- **Given** a batch planned with `--order priority` and again with `--order wsjf`
- **When** `sprint.py plan` runs
- **Then** every unit carries a `difficulty` object under both orders (tier/model absent while routing is disabled)
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py -k difficulty
- **Verified:** yes (2026-07-08)

### AC2: Tier and model appear only when routing is enabled

- **Given** a project config with `routing.enabled: true` and a model map
- **When** the plan runs
- **Then** each unit carries `tier` and `model` resolved via route.py; with routing disabled the plan JSON is unchanged apart from `difficulty`
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py -k routing_enabled
- **Verified:** yes (2026-07-08)

### AC3: Estimator failure degrades, never breaks planning

- **Given** a unit whose difficulty estimation raises
- **When** the plan runs
- **Then** that unit carries no routing fields and the plan completes for the rest of the batch
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py -k degrades
- **Verified:** yes (2026-07-08)

### AC4: Routing policy documented

- **Given** the reference docs
- **When** reviewed
- **Then** reference-sprint.md carries the routing policy, floors, escalation rule (retry once then escalate one declared tier, loop_guard cap unchanged) and the override-goes-to-ledger rule; reference-agent-prompt-template.md carries #tier-routing with the byte-identical-contract rule
- **Verify:** grep "tier-routing" .claude/skills/sdlc-studio/reference-agent-prompt-template.md
- **Verified:** yes (2026-07-08)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-08 | sprint: CR0190 | Created via `new` (deterministic) |
