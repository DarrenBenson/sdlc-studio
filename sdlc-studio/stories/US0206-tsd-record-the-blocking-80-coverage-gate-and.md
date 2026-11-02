# US0206: TSD: record the blocking 80% coverage gate and the bandit step in the coverage/security/quality-gate tables

> **Status:** Done
> **Created:** 2026-07-17
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** sdlc-studio/tsd.md
> **Epic:** EP0071
> **Points:** 2

## User Story

**As a** reader of the TSD
**I want** the blocking 80% coverage gate and the bandit step recorded in the coverage and quality-gate tables
**So that** the document states the gate CI enforces instead of claiming coverage is unwired

## Acceptance Criteria

### AC1: Coverage Targets, Coverage Measurement and the tools table record the blocking 80% CI coverage gate

- **Given** the TSD claimed coverage was "not currently wired into CI"
- **When** the blocking 80% coverage gate is recorded and reconciled with the ~90% aspiration
- **Then** Coverage Targets, Coverage Measurement and the tools table record the blocking 80% CI coverage gate, and Coverage Targets and Coverage Measurement each call the floor the hard gate; the ~90% aspiration the floor was first reconciled with was removed by US1102 and is named now only in the revision history
- **Verify:** grep "80% statement, the blocking CI floor" sdlc-studio/tsd.md
- **Verified:** yes (2026-07-17)

### AC2: Security Testing and both quality-gate tables record the blocking bandit step with its scope and

- **Given** the TSD claimed no dedicated security scanner was wired
- **When** the blocking bandit step is recorded with its scope and flags
- **Then** Security Testing and both quality-gate tables record the blocking bandit step with its scope and flags
- **Verify:** grep "bandit covers the shipped script tier only" sdlc-studio/tsd.md
- **Verified:** yes (2026-07-17)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-17 | sdlc-studio | Created via `new` (deterministic) |
| 2026-11-02 | Claude Opus 5.5 | BG1176: US1102 (d4028a31) removed both sentences the old greps read. AC1's Verify re-pointed at "80% statement, the blocking CI floor", which US1102 wrote, and AC2's at "bandit covers the shipped script tier only", a sentence of this story's own delivery (1efb2d81) that US1102 kept; AC2's text still holds. AC1's Then reworded: US1102 removed the ~90% aspiration, so there is no longer an aspiration for the floor to be reconciled with |
