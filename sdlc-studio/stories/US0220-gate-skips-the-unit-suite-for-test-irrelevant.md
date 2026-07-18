# US0220: gate skips the unit suite for test-irrelevant changes, named not silent

> **Status:** Draft
> **Created:** 2026-07-17
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/gate.py, tools/lint-style.sh
> **Epic:** EP0072
> **Depends on:** US0219
> **Points:** 3

## User Story

**As a** {{role}}
**I want** {{capability}}
**So that** {{benefit}}

## Acceptance Criteria

### AC1: A changed set with no test-relevant file skips the unit suite, named not silent

- **Given** {{context}}
- **When** {{action}}
- **Then** When the changed set contains NO file that can change a unit-test outcome (no `scripts/**/*.py`, no tracked artifact/config a test loads - e.g. only README/CHANGELOG/docs/reference-*/help/*), the gate SKIPS the Python unit suite while STILL running style/links/markdown/doc-coverage; the skip is named in the output, never silent.
- **Verify:** {{executable check}}

### AC2: Any code, artifact, or test change forces the full suite

- **Given** {{context}}
- **When** {{action}}
- **Then** A changed set containing any `scripts/**/*.py`, test file, or tracked artifact/config a test loads runs the full unit suite - the skip never applies.
- **Verify:** {{executable check}}

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-17 | sdlc-studio | Created via `new` (deterministic) |
| 2026-07-18 | sdlc-studio | Grooming: AC1/AC2 seeded from the criterion mis-filed on US0219; `Depends on: US0219` declared |
