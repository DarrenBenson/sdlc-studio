# US0226: rewrite US0166 AC3 as a two-file shell Verify with the missing shell prefix

> **Status:** Draft
> **Created:** 2026-07-17
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** sdlc-studio/stories/US0166-ship-a-stop-hook-installer-and-redefine-sprint.md
> **Epic:** EP0075
> **Points:** 2

## User Story

**As a** {{role}}
**I want** {{capability}}
**So that** {{benefit}}

## Acceptance Criteria

### AC1: AC3's Verify rewritten as shell command(s) checking both files for the close clause and the

- **Given** {{context}}
- **When** {{action}}
- **Then** AC3's Verify rewritten as shell command(s) checking both files for the close clause and the --require-close/Stop-hook enforcement text
- **Verify:** {{executable check}}

### AC2: The bare (non-shell) grep line corrected so no Verify passes via a dash-leading pattern accident

- **Given** {{context}}
- **When** {{action}}
- **Then** The bare (non-shell) grep line corrected so no Verify passes via a dash-leading pattern accident
- **Verify:** {{executable check}}

### AC3: Optional hardening: `verify_ac`'s grep verb refuses a pattern beginning with '-'

- **Given** {{context}}
- **When** {{action}}
- **Then** Optional hardening: `verify_ac`'s grep verb refuses a pattern beginning with '-'
- **Verify:** {{executable check}}

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-17 | sdlc-studio | Created via `new` (deterministic) |
