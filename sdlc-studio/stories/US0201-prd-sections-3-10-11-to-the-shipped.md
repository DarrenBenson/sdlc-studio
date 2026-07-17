# US0201: PRD sections 3/10/11 to the shipped Points model; Effort named only as retired; close BG0133/BG0136 and the plan-time-predictor open question

> **Status:** Draft
> **Created:** 2026-07-17
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** sdlc-studio/prd.md, sdlc-studio/trd.md
> **Epic:** EP0071
> **Points:** 3

## User Story

**As a** {{role}}
**I want** {{capability}}
**So that** {{benefit}}

## Acceptance Criteria

### AC1: prd.md Section 3's sizing row describes the shipped model: Fibonacci Points on stories/bugs

- **Given** {{context}}
- **When** {{action}}
- **Then** prd.md Section 3's sizing row describes the shipped model: Fibonacci Points on stories/bugs, T-shirt Size on CR/RFC/epic, forecast = sum(Points) x the measured tokens-per-point rate; Effort S/M/L named only as retired
- **Verify:** {{executable check}}

### AC2: prd.md Section 10 no longer claims the two loop defects are open; it cites BG0133/BG0136 as fixed

- **Given** {{context}}
- **When** {{action}}
- **Then** prd.md Section 10 no longer claims the two loop defects are open; it cites BG0133/BG0136 as fixed with the shipped behaviour (accuracy reads only the recorded forecast; `file_finding` accepts --affects)
- **Verify:** {{executable check}}

### AC3: prd.md Section 11's plan-time-predictor open question is closed citing RFC0038's points model

- **Given** {{context}}
- **When** {{action}}
- **Then** prd.md Section 11's plan-time-predictor open question is closed citing RFC0038's points model (r=+0.68)
- **Verify:** {{executable check}}

### AC4: trd.md §10 describes the points x measured-rate forecast with plan-time forecasts recorded to

- **Given** {{context}}
- **When** {{action}}
- **Then** trd.md §10 describes the points x measured-rate forecast with plan-time forecasts recorded to telemetry.forecasts stamped with estimator constants; §12 Q4 closed; §13's auto-recalibration Won't-Have restated to match the shipped per-plan rate recomputation
- **Verify:** {{executable check}}

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-17 | sdlc-studio | Created via `new` (deterministic) |
