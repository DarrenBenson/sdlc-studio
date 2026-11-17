# US1284: ADR-006 states the strength of its five-run evidence, names bad-plan propagation, and its instance count is tested

> **Status:** Draft
> **Risk-class:** standard
> **Delivers:** CR0724
> **Created:** 2026-11-17
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** sdlc-studio/trd.md, tools/tests/test_lean_trd_refresh.py
> **Epic:** EP0362
> **Points:** 2
> **Persona:** Abena Osei

## User Story

**As a** Abena Osei
**I want** ADR-006 states the strength of its five-run evidence, names bad-plan propagation, and its instance count is tested
**So that** CR0724 is delivered by work that can be planned and checked

## Acceptance Criteria

### AC1: ADR-006's Context states that the benchmark ran five times per cell and that the escape difference

- **Given** {{context}}
- **When** {{action}}
- **Then** {{observable outcome}}
- **Verify:** {{executable check}}

> Transcribed from the request: ADR-006's Context states that the benchmark ran five times per cell and that the escape difference is reportable but below conventional significance, in words that agree with D0014 in sdlc-studio/decisions.md and with docs/benchmarks/2026-07-08-n5-run.md

### AC2: ADR-006's Consequences name the bad-plan propagation failure mode recorded in D0014 as a negative

- **Given** {{context}}
- **When** {{action}}
- **Then** {{observable outcome}}
- **Verify:** {{executable check}}

> Transcribed from the request: ADR-006's Consequences name the bad-plan propagation failure mode recorded in D0014 as a negative, beside over-firing

### AC3: The Key Decisions bullet for ADR-006 gives a count of instances equal to the number of ADRs it then

- **Given** {{context}}
- **When** {{action}}
- **Then** {{observable outcome}}
- **Verify:** {{executable check}}

> Transcribed from the request: The Key Decisions bullet for ADR-006 gives a count of instances equal to the number of ADRs it then lists

### AC4: A test in tools/tests/`test_lean_trd_refresh.py` fails when the instance count in that bullet

- **Given** {{context}}
- **When** {{action}}
- **Then** {{observable outcome}}
- **Verify:** {{executable check}}

> Transcribed from the request: A test in tools/tests/`test_lean_trd_refresh.py` fails when the instance count in that bullet differs from the number of ADR ids listed after it

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-17 | sdlc-studio | Created via `new` (deterministic) |
