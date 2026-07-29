# US0559: The close reports its own cost - gate seconds and elapsed - so the next reduction is measured against a number rather than an impression

> **Status:** Ready
> **Delivers:** CR0498
> **Created:** 2026-07-29
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py
> **Epic:** EP0189
> **Points:** 3
> **Persona:** Maya Okafor

## User Story

**As a** an operator deciding whether the ceremony is getting cheaper
**I want** the close to report what it itself cost
**So that** the next reduction is judged against a recorded number instead of how long it felt

## Acceptance Criteria

### AC1: the close reports its gate seconds and its elapsed time

- **Given** a close that completes
- **When** it prints its result
- **Then** it reports the gate seconds it paid and the wall-clock elapsed across the ceremony, both read from recorded measurements rather than restated from prose
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::CloseCostReportTests::test_the_close_reports_its_gate_seconds_and_elapsed

### AC2: the cost is recorded on the run, not only printed

- **Given** a completed close
- **When** the run state is read afterwards
- **Then** the close's cost is on the record, so a later close can be compared with it
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::CloseCostReportTests::test_the_close_cost_is_recorded_on_the_run

### AC3: a close with a reused gate verdict reports the seconds it did not pay

- **Given** a close whose commits reused a gate verdict
- **When** it reports its cost
- **Then** the reused runs are counted, so a saving shows as a saving rather than as absent measurement
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::CloseCostReportTests::test_a_reused_verdict_is_reported_as_a_saving

### AC4: an unmeasured component is reported as unmeasured, never as zero

- **Given** a close where a cost component has no recorded measurement
- **When** the report is produced
- **Then** that component reads as unmeasured, and no total presents it as zero seconds
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::CloseCostReportTests::test_an_unmeasured_component_is_never_reported_as_zero

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-29 | sdlc-studio | Created via `new` (deterministic) |
| 2026-07-29 | Claude Opus 5 | Groomed: criteria authored against this story's slice, each with an executable Verify line |
