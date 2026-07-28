# US0535: The overhead ratio consumes recorded review durations, and states it is a lower bound only while a component is genuinely unmeasured

> **Status:** Ready
> **Delivers:** CR0466
> **Created:** 2026-07-28
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint_report.py
> **Epic:** EP0182
> **Points:** 3
> **Persona:** Maya Okafor

## User Story

**As a** an operator judging where sprint time goes
**I want** the overhead ratio to consume recorded review durations
**So that** the headline figure stops excluding the largest overhead component of the last two sprints

## Acceptance Criteria

### AC1: the ratio consumes recorded review durations

- **Given** a run whose review rounds carry durations
- **When** the overhead ratio is computed
- **Then** the review and repair component is measured from those durations rather than reported unmeasured
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py::OverheadReviewTermTests::test_recorded_round_durations_feed_the_overhead_term

### AC2: the lower-bound caveat is stated only while a component is genuinely unmeasured

- **Given** a run in which every overhead component is measured
- **When** the ratio is rendered
- **Then** it is not described as a floor, and a run with any unmeasured component still is
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py::OverheadReviewTermTests::test_the_floor_caveat_tracks_actual_unmeasured_components

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-28 | sdlc-studio | Created via `new` (deterministic) |
| 2026-07-28 | Claude Opus 5 | Groomed: criteria authored against this story's slice, each with an executable Verify line |
