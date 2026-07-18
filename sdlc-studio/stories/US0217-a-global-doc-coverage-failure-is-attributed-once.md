# US0217: a global doc-coverage failure is attributed once, not fanned across every unit

> **Status:** Draft
> **Created:** 2026-07-17
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/conformance.py, .claude/skills/sdlc-studio/scripts/gate.py
> **Epic:** EP0072
> **Depends on:** US0220
> **Points:** 3

## User Story

**As a** {{role}}
**I want** {{capability}}
**So that** {{benefit}}

## Acceptance Criteria

### AC1: When the 'documented' stage fails ONLY because of the global doc-coverage floor, conformance

- **Given** {{context}}
- **When** {{action}}
- **Then** When the 'documented' stage fails ONLY because of the global doc-coverage floor, conformance attributes it once as a global finding (naming the undocumented item) rather than fanning 'missing documented' across every unit; per-unit 'missing documented' is reserved for genuinely per-unit gaps.
- **Verify:** {{executable check}}

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-17 | sdlc-studio | Created via `new` (deterministic) |
