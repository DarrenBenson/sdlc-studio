# BG1330: 15 of RPT0028's 19 units have no priced cost of their own, because only a hand-run `lane return --agent` prices a unit, and the close counts no gap

> **Status:** Open
> **Severity:** Medium
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/sprint_report.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py
> **Evidence:** sdlc-studio/reports/RPT0028-sprint-report-run-01m7061x.md (per-unit table); RUN-01M7061X
> **Created:** 2026-11-10
> **Created-by:** sdlc-studio file
> **Raised-by:** Darren Benson (operator); human; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-10T12:22:17Z

## Summary

RPT0028's per-unit table reads 'NOT MEASURED - no agent returned for it was priced from its own transcript' for 15 of 19 units. Only US0986, US1130, US1133 and US1143, which the orchestrator put through `sprint.py lane return --units X --agent A` by hand on their second round, are priced. `sprint.py lane land` already takes the builder's id from its worktree name (agent-<id>) as the self-check author, but records no return, and the close reported 0 gaps. A per-unit cost forecast cannot be compared with actuals until each unit is priced.

## Steps to Reproduce

1. Deliver a unit through `sprint.py lane brief`, a builder agent in a worktree, `sprint.py lane land` and `sprint.py lane accept`, without running `lane return`.
2. Close the run.
3. Read the report's per-unit table: the unit's Dollars and Priced cells read NOT MEASURED, and the close lists no gap for it.

## Proposed Fix

`lane land` records the builder's return from its worktree's agent id when that agent's transcript is readable, or `lane accept` warns while a unit has none; the close lists each unpriced unit as a gap.

## Acceptance Criteria

- [ ] **AC1** The behaviour described is corrected: RPT0028's per-unit table reads 'NOT MEASURED - no agent returned for it was priced from its own transcript' for 15 of 19 units.
- [ ] **AC2** The proposed fix lands, pinned by a test: `lane land` records the builder's return from its worktree's agent id when that agent's transcript is readable, or `lane accept` warns while a unit has none...

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-10 | Darren Benson (operator) | Filed |
