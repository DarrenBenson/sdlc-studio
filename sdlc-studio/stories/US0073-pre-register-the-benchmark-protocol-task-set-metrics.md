# US0073: Pre-register the benchmark protocol: task set, metrics, baseline

> **Status:** Done
> **Created:** 2026-07-06
> **Created-by:** sdlc-studio new
> **Epic:** EP0017
> **Persona:** Sam Eriksson (QA)
> **Source:** CR-0178 (WS1), RFC-0025

## User Story

**As a** QA lead defending the tool's claims
**I want** the benchmark protocol pre-registered before any measured run
**So that** the result cannot be quietly reshaped and the comparison baseline is genuinely good

## Acceptance Criteria

### AC1: Protocol committed and frozen

- **Given** the task set, metrics, N and the baseline CLAUDE.md
- **When** they are committed before the first measured run
- **Then** git history shows the protocol unchanged between registration and publication
- **Verify:** manual review of the protocol file's git history

### AC2: Baseline is not a straw man

- **Given** the baseline arm's CLAUDE.md
- **When** a review seat that is NOT the harness author checks it
- **Then** it is signed off as genuinely good (a weak baseline fails this)
- **Verify:** manual review sign-off recorded

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-06 | sdlc | Created via `new` (deterministic) |
