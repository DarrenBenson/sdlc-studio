# US0206: TSD: record the blocking 80% coverage gate and the bandit step in the coverage/security/quality-gate tables

> **Status:** Draft
> **Created:** 2026-07-17
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** sdlc-studio/tsd.md
> **Epic:** EP0071
> **Points:** 2

## User Story

**As a** {{role}}
**I want** {{capability}}
**So that** {{benefit}}

## Acceptance Criteria

### AC1: Coverage Targets, Coverage Measurement and the tools table record the blocking 80% CI coverage gate

- **Given** the TSD claimed coverage was "not currently wired into CI"
- **When** the blocking 80% coverage gate is recorded and reconciled with the ~90% aspiration
- **Then** Coverage Targets, Coverage Measurement and the tools table record the blocking 80% CI coverage gate and reconcile the 80% floor with the ~90% aspiration
- **Verify:** grep "80% floor is the hard gate" sdlc-studio/tsd.md
- **Verified:** yes (2026-07-17)

### AC2: Security Testing and both quality-gate tables record the blocking bandit step with its scope and

- **Given** the TSD claimed no dedicated security scanner was wired
- **When** the blocking bandit step is recorded with its scope and flags
- **Then** Security Testing and both quality-gate tables record the blocking bandit step with its scope and flags
- **Verify:** grep "the script tier is scanned by bandit" sdlc-studio/tsd.md
- **Verified:** yes (2026-07-17)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-17 | sdlc-studio | Created via `new` (deterministic) |
