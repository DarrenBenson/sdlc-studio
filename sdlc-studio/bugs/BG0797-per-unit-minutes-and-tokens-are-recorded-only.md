# BG0797: Per-unit minutes and tokens are recorded only on an In Progress transition the lean loop never makes, and the report does not say why the column is empty

> **Status:** Open
> **Severity:** Medium
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/lib/run_state.py, .claude/skills/sdlc-studio/scripts/critic.py, .claude/skills/sdlc-studio/scripts/sprint_report.py, .claude/skills/sdlc-studio/scripts/tests/test_run_state.py, .claude/skills/sdlc-studio/scripts/tests/test_critic.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py
> **Created:** 2026-09-27
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-09-27T07:29:13Z

## Summary

`run_state.record_unit_actual` opens a unit's span only on a move to In Progress and closes it at a terminal status. Sprint 5's units went from Draft straight to Done at landing, so all 37 read NOT MEASURED - not recorded, and the report gives no reason or remedy; the estimate-accuracy promise (points, time and tokens per unit) is unmet for every lean run.

## Steps to Reproduce

RPT0010 per-unit table: 37 of 37 NOT MEASURED - not recorded; sdlc-studio/.local/run-state.json has no `unit_actuals` entries.

## Proposed Fix

Open a unit's span when its build is dispatched or its first verify or verdict is recorded (a lean-loop event that always happens), keep In Progress as one trigger, and have the report name the cause when no span was recorded.

## Acceptance Criteria

- [ ] **AC1** The behaviour described is corrected: `run_state.record_unit_actual` opens a unit's span only on a move to In Progress and closes it at a terminal status.
- [ ] **AC2** Following the recorded steps no longer reproduces the defect: RPT0010 per-unit table: 37 of 37 NOT MEASURED - not recorded; sdlc-studio/.local/run-state.json has no `unit_actuals` entries.
- [ ] **AC3** The proposed fix lands, pinned by a test: Open a unit's span when its build is dispatched or its first verify or verdict is recorded (a lean-loop event that always happens), keep In Progress as one...

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-27 | sdlc-studio | Filed |
