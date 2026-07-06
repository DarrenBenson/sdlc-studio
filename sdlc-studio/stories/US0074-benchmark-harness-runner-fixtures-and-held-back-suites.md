# US0074: Benchmark harness runner, fixtures and held-back suites

> **Status:** Draft
> **Created:** 2026-07-06
> **Created-by:** sdlc-studio new
> **Epic:** EP0017
> **Persona:** Sam Eriksson (QA)
> **Source:** CR-0178 (WS2), RFC-0025

## User Story

**As a** QA lead
**I want** a repeatable harness with fixture repos and held-back acceptance suites
**So that** defect escapes are measured by an oracle, not judged, and runs are reproducible

## Acceptance Criteria

### AC1: One-command reproducible run

- **Given** a clean clone
- **When** the harness runs
- **Then** it drives both arms over the fixtures and captures tokens, wall time, defect escapes
  (held-back suite verdict) and rework rate automatically, no hand-scoring
- **Verify:** tools/bench runner exits 0 on the fixtures

### AC2: Fixtures and hidden suites versioned in-repo

- **Given** the fixture repos
- **When** the harness runs
- **Then** the agent never sees the hidden suites, which live under version control with the harness
- **Verify:** manual review of the fixture/suite separation

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-06 | sdlc | Created via `new` (deterministic) |
