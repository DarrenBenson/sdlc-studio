# US1181: Recording a REJECT says the rejecting reviewer is needed for round 2, and the runbook row says how to keep it resumable

> **Status:** Draft
> **Risk-class:** standard
> **Delivers:** CR0639
> **Created:** 2026-11-17
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/critic.py, .claude/skills/sdlc-studio/reference-sprint-toolchain.md, .claude/skills/sdlc-studio/scripts/tests/test_critic_record_reject_round2.py
> **Epic:** EP0320
> **Points:** 2
> **Persona:** Abena Osei

## User Story

**As a** Abena Osei
**I want** Recording a REJECT says the rejecting reviewer is needed for round 2, and the runbook row says how to keep it resumable
**So that** CR0639 is delivered by work that can be planned and checked

## Acceptance Criteria

### AC1: Given the toolchain runbook's review step, when an orchestrator reads it, then it says a REJECTing

- **Given** {{context}}
- **When** {{action}}
- **Then** {{observable outcome}}
- **Verify:** {{executable check}}

> Transcribed from the request: Given the toolchain runbook's review step, when an orchestrator reads it, then it says a REJECTing reviewer's worktree is kept until that unit's round 2 is recorded, and names what to do when it is gone (a fresh instance of the same seat on `critic.py brief --rejoinder`)

### AC2: Given a REJECT recorded through `critic.py record`, when it is written, then the command's output

- **Given** {{context}}
- **When** {{action}}
- **Then** {{observable outcome}}
- **Verify:** {{executable check}}

> Transcribed from the request: Given a REJECT recorded through `critic.py record`, when it is written, then the command's output says the rejecting reviewer is needed for round 2

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-17 | sdlc-studio | Created via `new` (deterministic) |
