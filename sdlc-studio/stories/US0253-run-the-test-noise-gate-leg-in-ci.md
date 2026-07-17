# US0253: run the test-noise gate leg in CI and broaden the leak detector beyond one shape

> **Status:** Draft
> **Created:** 2026-07-17
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .github/workflows/lint.yml, sdlc-studio/tsd.md
> **Epic:** EP0082
> **Points:** 3

## User Story

**As a** {{role}}
**I want** {{capability}}
**So that** {{benefit}}

## Acceptance Criteria

### AC1: CI runs the noise leg (skill-tests.sh or an equivalent step in lint.yml/npm test) so a leaked

- **Given** {{context}}
- **When** {{action}}
- **Then** CI runs the noise leg (skill-tests.sh or an equivalent step in lint.yml/npm test) so a leaked diagnostic fails the build, not just the opt-in hook
- **Verify:** {{executable check}}

### AC2: The detector catches the common leak shapes ('ERROR:', 'WARNING:', 'script: ERROR', traceback

- **Given** {{context}}
- **When** {{action}}
- **Then** The detector catches the common leak shapes ('ERROR:', 'WARNING:', 'script: ERROR', traceback lines), with an allowlist for intentional output
- **Verify:** {{executable check}}

### AC3: tsd.md's wording matches where the gate actually runs

- **Given** {{context}}
- **When** {{action}}
- **Then** tsd.md's wording matches where the gate actually runs
- **Verify:** {{executable check}}

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-17 | sdlc-studio | Created via `new` (deterministic) |
