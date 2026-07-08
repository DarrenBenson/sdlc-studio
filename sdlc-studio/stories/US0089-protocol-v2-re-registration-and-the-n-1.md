# US0089: Protocol v2 re-registration and the N=1 re-spike

> **Status:** Draft
> **Created:** 2026-07-08
> **Created-by:** sdlc-studio new
> **Epic:** EP0017
> **Persona:** Sam Eriksson (QA)
> **CR:** CR-0193
> **Depends on:** US0086, US0087, US0088

## User Story

**As a** benchmark operator honouring the anti-hype stance
**I want** a superseding pre-registration and a fresh N=1 spike over the redesigned benchmark
**So that** the fixture-set change is made openly and the redesign is proven able to differentiate before any N=5 spend

## Acceptance Criteria

### AC1: Protocol v2 pre-registered without touching v1's frozen body

- **Given** docs/benchmarks/protocol-v2.md
- **When** committed before the re-spike
- **Then** it pre-registers arms A/B/R, the tiered task set, five metrics (incl. Auditability), N (Tier 1 N=5 / Tier 2 N=2), the calibration rule and the cut order; v1 gains only a superseded status line
- **Verify:** pytest tools/tests/test_benchmark_protocol.py -k v2

### AC2: Re-spike runs 3 arms x 2 Tier-1 fixtures

- **Given** prepared, environmentally-isolated workspaces
- **When** the 6 live runs + audit quizzes complete
- **Then** all results (including whether arm A/R actually engaged the pipeline) are recorded via the harness with automatic metrics capture
- **Verify:** manual review of tools/bench/results/runs.jsonl for the 6 re-spike rows

### AC3: Published regardless, with the cost index

- **Given** the results (flattering or not)
- **When** the report is written to docs/benchmarks/
- **Then** it carries per-tier raw data, min/max, metrics_source disclosure, arm R's cost index, reviewer-independence as a descriptive note, and an explicit N=5 go/no-go recommendation
- **Verify:** manual review of the published report

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-08 | sprint: CR0193 | Created via `new` (deterministic) |
