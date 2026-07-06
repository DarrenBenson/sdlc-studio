# US0075: First measured benchmark run and published report

> **Status:** Draft
> **Created:** 2026-07-06
> **Created-by:** sdlc-studio new
> **Epic:** EP0017
> **Persona:** Sam Eriksson (QA)
> **Source:** CR-0178 (WS3), RFC-0025

## User Story

**As a** QA lead honouring the anti-hype stance
**I want** a first measured run published regardless of outcome
**So that** the tool's claims rest on honest numbers, and the whole v4 premise is validated early

## Acceptance Criteria

### AC1: De-risking spike first, then the run

- **Given** the frozen protocol
- **When** an N=1 spike runs across the fixtures, then N=5
- **Then** the spike gives an early effect-size read before the full cost is committed
- **Verify:** manual review of the spike output

### AC2: Published with raw data and error bars, either way

- **Given** the results (flattering or not)
- **When** the report is written to docs/benchmarks/
- **Then** it carries raw per-run data and honest error bars, and an unflattering result does not
  block publication
- **Verify:** manual review of the published report

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-06 | sdlc | Created via `new` (deterministic) |
