# US0174: The sprint report: deterministic composition of delivered, actual spend, accuracy, lessons, tickets, models

> **Status:** Done
> **Created:** 2026-07-16
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint_report.py
> **Epic:** EP0048
> **Points:** 5

## User Story

**As an** operator closing a sprint
**I want** a deterministic report of what shipped, what it cost, and whether the estimate held
**So that** I get a CAB-grade summary at no model-token cost

## Acceptance Criteria

### AC1: the report composes delivered points, spend with rework, tickets and lessons; an interactive batch says so rather than reporting zero dollars

- **Given** a retro with delivered pointed units, some with per-attempt telemetry and some without
- **When** `sprint_report.report` composes it
- **Then** it reports the delivered points, the true spend summed over attempts, the tickets raised and the lessons, and an interactive batch (no token telemetry) says so instead of a false $0
- **Verify:** shell python3 -m unittest discover -s .claude/skills/sdlc-studio/scripts/tests -p test_sprint_report.py -k Composition
- **Verified:** yes (2026-07-16)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-16 | sdlc-studio | Created via `new` (deterministic) |
