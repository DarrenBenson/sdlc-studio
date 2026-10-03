# CR-0605: A unit built through a lane opens and closes its own span, so the report measures per-unit minutes

> **Status:** Complete
> **Decomposed-into:** EP0271
> **Priority:** Medium
> **Type:** Improvement
> **Size:** S
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_lean_lane_unit_span.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py
> **Date:** 2026-10-02
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-10-02T07:27:59Z

## Summary

RPT0014 reads NOT MEASURED for 29 of 34 units' minutes and tokens: units built through sprint lane brief/return never pass through In Progress, so they have no span, while the four that did opened at the run's start and closed at the seal, so their 436-546 minutes are the whole run, not their work. Per-unit cost is unreadable for a lane-driven run.

## Impact

Maya reads a sprint report whose per-unit cost table is empty or misleading, so estimates never calibrate per unit.

## Acceptance Criteria

- [ ] Given a unit in the open run's batch, when `sprint lane brief --units X` is issued and later `sprint lane return --units X` passes, then the unit's span opens at the brief and closes at the return, and the page reports minutes for it measured over that span, with no new flag or refusal. Fails on: the current code opens no span
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_lane_unit_span.py::LaneUnitSpanTests::test_a_lane_brief_and_return_measure_the_unit

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-02 | sdlc-studio | Raised |
