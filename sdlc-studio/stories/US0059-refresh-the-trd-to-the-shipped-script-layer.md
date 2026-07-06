# US0059: Refresh the TRD to the shipped script layer and write contract with a freshness guard

> **Status:** Done
> **Created:** 2026-07-06
> **Created-by:** sdlc-studio new
> **Epic:** EP0012
> **Persona:** Skill Maintainer
> **Source:** CR-0184
> **Depends on:** US0055, US0056, US0058

## User Story

**As a** maintainer or a rebuilding agent
**I want** the TRD to match the shipped script layer, write contract and state files
**So that** the rebuild blueprint is trustworthy and its stale write-contract claims cannot mislead

## Acceptance Criteria

### AC1: Blueprint matches the code

- **Given** the shipped v3.5.0+ scripts (43 top-level, the real write surface)
- **When** the TRD is read
- **Then** its component counts, script-contract write surface, state-file inventory and test
  figures match the code, and the "read-only over the workspace" claim is corrected
- **Verify:** manual review against the cited files

### AC2: A freshness guard prevents re-rot

- **Given** a future TRD scale/contract claim that drifts from code
- **When** the guard runs
- **Then** it flags the stale claim (as LATEST.md claims are guarded)
- **Verify:** python3 tools/tests then discover the new TRD-freshness test

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-06 | sdlc | Created via `new` (deterministic) |
