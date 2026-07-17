# US0205: TRD ADR-008 ULID: state the real 6+2-char guarantee and cross-machine residual risk; drop the collision-free absolute

> **Status:** Draft
> **Created:** 2026-07-17
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** sdlc-studio/trd.md
> **Epic:** EP0071
> **Points:** 2

## User Story

**As a** {{role}}
**I want** {{capability}}
**So that** {{benefit}}

## Acceptance Criteria

### AC1: §6, ADR-008 and §8 state the actual guarantee: 6+2 chars, ~1/1024 per pair inside a ~17-minute

- **Given** {{context}}
- **When** {{action}}
- **Then** §6, ADR-008 and §8 state the actual guarantee: 6+2 chars, ~1/1024 per pair inside a ~17-minute window, glob-retry as the single-writer local backstop
- **Verify:** {{executable check}}

### AC2: ADR-008 gains a residual-risk paragraph covering the cross-machine case and naming `next_id.py`'s

- **Given** {{context}}
- **When** {{action}}
- **Then** ADR-008 gains a residual-risk paragraph covering the cross-machine case and naming `next_id.py`'s collisions detector as the merge-time guard
- **Verify:** {{executable check}}

### AC3: The ADR title no longer claims 'collision-free' unconditionally

- **Given** {{context}}
- **When** {{action}}
- **Then** The ADR title no longer claims 'collision-free' unconditionally
- **Verify:** {{executable check}}

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-17 | sdlc-studio | Created via `new` (deterministic) |
