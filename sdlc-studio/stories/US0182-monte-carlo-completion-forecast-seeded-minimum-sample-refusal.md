# US0182: Monte Carlo completion forecast (seeded, minimum-sample refusal) surfaced in sprint report, schedule-vs-cost doc

> **Status:** Done
> **Created:** 2026-07-16
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/flow.py, .claude/skills/sdlc-studio/scripts/sprint_report.py, .claude/skills/sdlc-studio/reference-sprint.md
> **Epic:** EP0052
> **Depends on:** US0180
> **Points:** 3

## User Story

**As** Maya Okafor (solo founder-engineer, the Primary)
**I want** a probabilistic completion forecast for a named batch, from measured throughput
**So that** I get an honest 'when' (50/85/95% confidence dates) instead of a single-point guess

## Acceptance Criteria

### AC1: Seeded Monte Carlo over measured weekly throughput

- **Given** a workspace with at least the minimum throughput history
- **When** forecast runs for a named batch
- **Then** 50/85/95% completion dates are produced from a seeded, reproducible simulation
- **Verify:** shell python3 -m unittest discover -s .claude/skills/sdlc-studio/scripts/tests/ -p test_flow.py -k MonteCarlo
- **Verified:** yes (2026-07-16)

### AC2: Refuses under minimum sample size

- **Given** a workspace with too little history
- **When** forecast runs
- **Then** it refuses with the sample size named - never a guessed date
- **Verify:** shell python3 -m unittest discover -s .claude/skills/sdlc-studio/scripts/tests/ -p test_flow.py -k MinimumSample
- **Verified:** yes (2026-07-16)

### AC3: Sprint report and doc separation of instruments

- **Given** a sprint report render and a reference reader
- **When** the report shows flow numbers
- **Then** documentation states flow answers schedule, points x rate answers cost, and neither feeds a gate
- **Verify:** grep "schedule" .claude/skills/sdlc-studio/reference-sprint.md
- **Verified:** yes (2026-07-16)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-16 | sdlc-studio | Created via `new` (deterministic) |
