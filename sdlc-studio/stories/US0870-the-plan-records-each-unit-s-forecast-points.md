# US0870: The plan records each unit's forecast points, minutes and tokens, and nothing later overwrites it

> **Status:** In Progress
> **Created:** 2026-09-23
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/lib/run_state.py, .claude/skills/sdlc-studio/scripts/tests/test_lean_plan_snapshot.py
> **Epic:** EP0260
> **Points:** 3
> **Persona:** Maya Okafor

## User Story

**As a** operator judging estimate accuracy
**I want** each unit's planned points, minutes and tokens frozen at plan time
**So that** the report compares the actuals with what was planned, not with sizes resized along the way

## Acceptance Criteria

- **AC1:** Given a batch of units with points, when sprint plan --write runs, then run state key `plan_snapshot` records per unit its planned points, forecast tokens (points times the token rate) and forecast minutes (points times the minute rate, or not measured), plus both rates and their sources
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_plan_snapshot.py::PlanSnapshotTests::test_the_plan_records_a_three_way_forecast_per_unit
- **AC2:** Given a written plan, when a unit's Points field is later resized on disk, then its planned points in `plan_snapshot` are unchanged and `run_state` exposes both planned and current points
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_plan_snapshot.py::PlanSnapshotTests::test_resizing_a_unit_leaves_the_planned_points_unchanged
- **AC3:** Given a unit added with sprint batch add after the plan, when it is added, then it gets its own forecast row marked added, and the original plan's totals are unchanged
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_plan_snapshot.py::PlanSnapshotTests::test_an_added_unit_is_forecast_and_marked_added

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-23 | sdlc-studio | Created via `new` (deterministic) |
