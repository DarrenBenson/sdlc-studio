# US0213: verify_ac freshness fingerprints the AC section, not the file mtime

> **Status:** Draft
> **Created:** 2026-07-17
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/verify_ac.py
> **Epic:** EP0072
> **Points:** 3

## User Story

**As a** {{role}}
**I want** {{capability}}
**So that** {{benefit}}

## Acceptance Criteria

### AC1: A status-only or metadata-only edit leaves a green verify entry fresh (AC-section hash unchanged)

- **Given** {{context}}
- **When** {{action}}
- **Then** A status-only or metadata-only edit leaves a green verify entry fresh (AC-section hash unchanged)
- **Verify:** {{executable check}}

### AC2: Any edit inside the Acceptance Criteria section still invalidates it

- **Given** {{context}}
- **When** {{action}}
- **Then** Any edit inside the Acceptance Criteria section still invalidates it
- **Verify:** {{executable check}}

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-17 | sdlc-studio | Created via `new` (deterministic) |
