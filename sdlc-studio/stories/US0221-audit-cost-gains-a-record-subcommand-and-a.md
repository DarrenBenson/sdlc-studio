# US0221: audit_cost gains a record subcommand and a committed evidence ledger; estimate from measured medians with a named fallback

> **Status:** Draft
> **Created:** 2026-07-17
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/audit_cost.py, .claude/skills/sdlc-studio/reference-audit.md
> **Epic:** EP0073
> **Points:** 5

## User Story

**As a** {{role}}
**I want** {{capability}}
**So that** {{benefit}}

## Acceptance Criteria

### AC1: `audit_cost.py` gains a 'record' subcommand appending {date, lenses, rounds, votes, estimated

- **Given** {{context}}
- **When** {{action}}
- **Then** `audit_cost.py` gains a 'record' subcommand appending {date, lenses, rounds, votes, estimated agents/tokens, actual agents/tokens/minutes, notes} to a committed evidence ledger
- **Verify:** {{executable check}}

### AC2: When ledger entries exist, the estimate is derived from measured medians (falling back to the

- **Given** {{context}}
- **When** {{action}}
- **Then** When ledger entries exist, the estimate is derived from measured medians (falling back to the shipped constants) and the output names which basis it used
- **Verify:** {{executable check}}

### AC3: reference-audit.md#audit-preflight step 4 instructs recording actuals via the subcommand, not just

- **Given** {{context}}
- **When** {{action}}
- **Then** reference-audit.md#audit-preflight step 4 instructs recording actuals via the subcommand, not just reporting them in chat
- **Verify:** {{executable check}}

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-17 | sdlc-studio | Created via `new` (deterministic) |
