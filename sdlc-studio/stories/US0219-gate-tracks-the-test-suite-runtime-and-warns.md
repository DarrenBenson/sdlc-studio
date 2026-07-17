# US0219: gate tracks the test-suite runtime and warns before a long run

> **Status:** Draft
> **Created:** 2026-07-17
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/gate.py
> **Epic:** EP0072
> **Points:** 3

## User Story

**As a** {{role}}
**I want** {{capability}}
**So that** {{benefit}}

## Acceptance Criteria

> Seeded from the request's full criteria list - redistribute across this epic's stories as you groom them.

### AC1: The gate records each run's test-suite wall-time to a rolling local history

- **Given** {{context}}
- **When** {{action}}
- **Then** The gate records each run's test-suite wall-time to a rolling local history.
- **Verify:** {{executable check}}

### AC2: Before running the suite the gate estimates duration from that history and prints a warning when it

- **Given** {{context}}
- **When** {{action}}
- **Then** Before running the suite the gate estimates duration from that history and prints a warning when it exceeds a configurable threshold (e.g. `gate.warn_seconds)`, so a long run is expected, not a surprise timeout.
- **Verify:** {{executable check}}

### AC3: When the changed set contains NO file that can change a unit-test outcome (no scripts/**/*.py, no

- **Given** {{context}}
- **When** {{action}}
- **Then** When the changed set contains NO file that can change a unit-test outcome (no scripts/**/*.py, no tracked artifact/config a test loads - e.g. only README/CHANGELOG/docs/reference-*/help/*), the gate SKIPS the Python unit suite while STILL running style/links/markdown/doc-coverage; the skip is named in the output, never silent, and any code/artifact/test change forces the full suite.
- **Verify:** {{executable check}}

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-17 | sdlc-studio | Created via `new` (deterministic) |
