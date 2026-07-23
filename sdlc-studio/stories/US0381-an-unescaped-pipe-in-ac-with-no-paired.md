# US0381: an unescaped pipe in --ac with no paired --verify is warned or refused by name, correctly-paired output byte-identical

> **Status:** Draft
> **Delivers:** CR0381
> **Created:** 2026-07-23
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Epic:** EP0139
> **Points:** 2

## User Story

**As a** {{role}}
**I want** {{capability}}
**So that** {{benefit}}

## Acceptance Criteria

### AC1: An --ac value containing an unescaped pipe, passed without a paired --verify, is refused or warned

- **Given** {{context}}
- **When** {{action}}
- **Then** An --ac value containing an unescaped pipe, passed without a paired --verify, is refused or warned about by name, rather than written out as prose
- **Verify:** {{executable check}}

### AC2: A correctly paired --ac/--verify remains byte-identical to today's output, so the guard adds a

- **Given** {{context}}
- **When** {{action}}
- **Then** A correctly paired --ac/--verify remains byte-identical to today's output, so the guard adds a warning and changes no working path
- **Verify:** {{executable check}}

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-23 | sdlc-studio | Created via `new` (deterministic) |
