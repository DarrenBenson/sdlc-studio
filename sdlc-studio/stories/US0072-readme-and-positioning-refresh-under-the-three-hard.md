# US0072: README and positioning refresh under the three hard constraints

> **Status:** Draft
> **Created:** 2026-07-06
> **Created-by:** sdlc-studio new
> **Epic:** EP0017
> **Persona:** Orchestrator / Operator
> **Source:** CR-0177

## User Story

**As a** prospective adopter reading the README
**I want** the headline framed around the two differentiators as proof of the anti-vibe-coding philosophy
**So that** the tool reads as a category of one, with greenfield and brownfield equally visible

## Acceptance Criteria

### AC1: The three hard constraints hold

- **Given** the reframed README
- **When** it is reviewed
- **Then** (a) anti-vibe-coding is the umbrella with brownfield+reconcile as proof, (b) greenfield
  stays an equally visible front door, (c) the command catalogue moves below the fold
- **Verify:** manual review against the three constraints

### AC2: No claim outruns a shipped feature

- **Given** the new copy
- **When** claims are checked
- **Then** the team-shape story appears only after the schema CRs ship, the on-ramp mention lands with
  CR0175, and style/neutrality gates pass
- **Verify:** npm run lint

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-06 | sdlc | Created via `new` (deterministic) |
