# US0373: decompose critiqued into its named halves in the report and correct the remedy line

> **Status:** Draft
> **Delivers:** CR0368
> **Created:** 2026-07-23
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Epic:** EP0132
> **Points:** 3

## User Story

**As a** {{role}}
**I want** {{capability}}
**So that** {{benefit}}

## Acceptance Criteria

### AC1: Given a unit missing only the reviewer-of-record sign-off, when conformance reports it, then the

- **Given** {{context}}
- **When** {{action}}
- **Then** Given a unit missing only the reviewer-of-record sign-off, when conformance reports it, then the output names the sign-off specifically rather than the composite stage
- **Verify:** {{executable check}}

### AC2: Given a unit missing several halves at once, when conformance reports it, then every unmet half is

- **Given** {{context}}
- **When** {{action}}
- **Then** Given a unit missing several halves at once, when conformance reports it, then every unmet half is named in one line, not just the first
- **Verify:** {{executable check}}

### AC3: Given a unit whose critiqued stage is satisfied, when conformance runs, then it is reported

- **Given** {{context}}
- **When** {{action}}
- **Then** Given a unit whose critiqued stage is satisfied, when conformance runs, then it is reported conformant exactly as today - the change is diagnostic detail, not a new refusal
- **Verify:** {{executable check}}

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-23 | sdlc-studio | Created via `new` (deterministic) |
