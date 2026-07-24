# US0378: a no-subcommand status prints the pillars and exits 0, explicit subcommands unchanged

> **Status:** Draft
> **Delivers:** CR0375
> **Created:** 2026-07-23
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Epic:** EP0136
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/scripts/status.py, .claude/skills/sdlc-studio/scripts/tests/test_status.py

## User Story

**As a** {{role}}
**I want** {{capability}}
**So that** {{benefit}}

## Acceptance Criteria

### AC1: python3 status.py with no subcommand prints the pillars dashboard and exits 0, exactly as status.py

- **Given** {{context}}
- **When** {{action}}
- **Then** python3 status.py with no subcommand prints the pillars dashboard and exits 0, exactly as status.py pillars does
- **Verify:** {{executable check}}

### AC2: explicit subcommands and their flags behave unchanged

- **Given** {{context}}
- **When** {{action}}
- **Then** explicit subcommands and their flags behave unchanged
- **Verify:** {{executable check}}

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-23 | sdlc-studio | Created via `new` (deterministic) |
