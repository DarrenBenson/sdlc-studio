# US1304: The sprint report counts lines added and removed in the batch's declared files over a named commit range, and states priced cost per delivered line beside cost per point

> **Status:** Draft
> **Risk-class:** standard
> **Delivers:** CR0734
> **Created:** 2026-11-17
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint_report.py, .claude/skills/sdlc-studio/help/sprint.md, tools/tests/test_sprint_report_cost_per_line.py
> **Epic:** EP0371
> **Points:** 3
> **Persona:** Abena Osei

## User Story

**As a** Abena Osei
**I want** The sprint report counts lines added and removed in the batch's declared files over a named commit range, and states priced cost per delivered line beside cost per point
**So that** CR0734 is delivered by work that can be planned and checked

## Acceptance Criteria

### AC1: The report states lines added and lines removed over the run's commits, counted only in files the

- **Given** {{context}}
- **When** {{action}}
- **Then** {{observable outcome}}
- **Verify:** {{executable check}}

> Transcribed from the request: The report states lines added and lines removed over the run's commits, counted only in files the batch's units declare in Affects, with artefact and changelog paths excluded and the exclusion named

### AC2: The report states priced cost per delivered line (added plus removed) beside cost per point, and

- **Given** {{context}}
- **When** {{action}}
- **Then** {{observable outcome}}
- **Verify:** {{executable check}}

> Transcribed from the request: The report states priced cost per delivered line (added plus removed) beside cost per point, and omits the figure with a reason when the run has no priced cost or no counted lines

### AC3: The figure is recomputable: the report names the commit range it counted

- **Given** {{context}}
- **When** {{action}}
- **Then** {{observable outcome}}
- **Verify:** {{executable check}}

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-17 | sdlc-studio | Created via `new` (deterministic) |
