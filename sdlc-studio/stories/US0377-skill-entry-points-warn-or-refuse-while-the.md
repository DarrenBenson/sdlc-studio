# US0377: skill entry points warn or refuse while the inflight sidecar exists, own processes exempt, a stale sidecar still recovers

> **Status:** Draft
> **Delivers:** CR0374
> **Created:** 2026-07-23
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Epic:** EP0135
> **Points:** 3

## User Story

**As a** {{role}}
**I want** {{capability}}
**So that** {{benefit}}

## Acceptance Criteria

### AC1: a skill script entry point invoked while mutation-inflight.json exists prints a loud warning naming

- **Given** {{context}}
- **When** {{action}}
- **Then** a skill script entry point invoked while mutation-inflight.json exists prints a loud warning naming the mutated file (or refuses, for write-path scripts), so concurrent execution of a mutant is visible instead of silent
- **Verify:** {{executable check}}

### AC2: the mutation run's own processes are exempt, and a stale sidecar (the recovery case) still recovers

- **Given** {{context}}
- **When** {{action}}
- **Then** the mutation run's own processes are exempt, and a stale sidecar (the recovery case) still recovers exactly as today
- **Verify:** {{executable check}}

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-23 | sdlc-studio | Created via `new` (deterministic) |
