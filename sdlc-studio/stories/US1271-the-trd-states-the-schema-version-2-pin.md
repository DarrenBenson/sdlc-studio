# US1271: The TRD states the schema version 2 pin and the sequential era's remote scan and fetch-first defence

> **Status:** Draft
> **Risk-class:** standard
> **Delivers:** CR0717
> **Created:** 2026-11-17
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** sdlc-studio/trd.md, tools/tests/test_lean_trd_refresh.py
> **Epic:** EP0356
> **Points:** 3
> **Persona:** Abena Osei

## User Story

**As a** Abena Osei
**I want** The TRD states the schema version 2 pin and the sequential era's remote scan and fetch-first defence
**So that** CR0717 is delivered by work that can be planned and checked

## Acceptance Criteria

### AC1: Section 6 or ADR-008 of the TRD states that this repository is pinned to schema version 2, with the

- **Given** {{context}}
- **When** {{action}}
- **Then** {{observable outcome}}
- **Verify:** {{executable check}}

> Transcribed from the request: Section 6 or ADR-008 of the TRD states that this repository is pinned to schema version 2, with the reason, citing the pin in `sdlc-studio/.config.yaml`.

### AC2: The TRD describes the sequential era's concurrency defence: the remote scan by `next_id.py` with

- **Given** {{context}}
- **When** {{action}}
- **Then** {{observable outcome}}
- **Verify:** {{executable check}}

> Transcribed from the request: The TRD describes the sequential era's concurrency defence: the remote scan by `next_id.py` with `--remote`, its scan states, the local-only fallback warning and the fetch-first precondition, each matching the script's behaviour.

### AC3: The TRD distinguishes the seeded schema version for a new project from the fallback an unstamped

- **Given** {{context}}
- **When** {{action}}
- **Then** {{observable outcome}}
- **Verify:** {{executable check}}

> Transcribed from the request: The TRD distinguishes the seeded schema version for a new project from the fallback an unstamped workspace resolves to, naming both template files.

### AC4: A test in `tools/tests/test_lean_trd_refresh.py` fails when the TRD omits the remote scan or states

- **Given** {{context}}
- **When** {{action}}
- **Then** {{observable outcome}}
- **Verify:** {{executable check}}

> Transcribed from the request: A test in `tools/tests/test_lean_trd_refresh.py` fails when the TRD omits the remote scan or states a pinned schema version different from the one in `sdlc-studio/.config.yaml`.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-17 | sdlc-studio | Created via `new` (deterministic) |
