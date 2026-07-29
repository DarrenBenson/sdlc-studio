# US0533: The gate attributes its seconds per lane, so a lane that becomes the dominant cost is visible without profiling it by hand

> **Status:** Ready
> **Delivers:** CR0465
> **Created:** 2026-07-28
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/gate.py, .claude/skills/sdlc-studio/scripts/tests/test_gate.py
> **Epic:** EP0181
> **Points:** 3
> **Persona:** Maya Okafor

## User Story

**As a** an operator deciding where to spend gate-time budget
**I want** the gate to report its seconds per lane
**So that** I can see which lane became the cost without profiling it by hand

## Acceptance Criteria

### AC1: the gate reports its seconds per lane

- **Given** a gate run in which one lane dominates the elapsed time
- **When** the gate reports
- **Then** each lane's own seconds are named beside it and the dominant lane is identified, so a lane becoming the cost is visible without profiling by hand
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_gate.py::LaneCostAttributionTests::test_each_lane_reports_its_own_seconds

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-28 | sdlc-studio | Created via `new` (deterministic) |
| 2026-07-28 | Claude Opus 5 | Groomed: criteria authored against this story's slice, each with an executable Verify line |
