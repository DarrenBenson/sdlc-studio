# US0524: An unmeasured component is reported as unmeasured rather than as zero, and the ratio is written to the velocity record

> **Status:** Done
> **Delivers:** CR0462
> **Created:** 2026-07-28
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint_report.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py
> **Epic:** EP0179
> **Points:** 3
> **Persona:** Maya Okafor

## User Story

**As a** reader of a velocity record that has to be trustworthy to be useful
**I want** an unmeasured component reported as unmeasured and the ratio written to the velocity record
**So that** a missing measurement never reads as a cheap one, and the trend across sprints is visible

## Acceptance Criteria

### AC1: an unmeasured component is reported as unmeasured, never as zero

- **Given** a run with one timing component absent
- **When** the close reports
- **Then** that component reads as unmeasured and the ratio states which part it excludes - a plausible number that is not the truth is worse than an absent one
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py::OverheadRatioTests::test_an_unmeasured_component_is_not_zero
- **Verified:** yes (2026-07-28)

### AC2: the ratio is written to the velocity record so the trend is readable

- **Given** a closed run
- **When** the close completes
- **Then** the ratio joins the velocity record, because a single sprint's ratio says little and the direction says everything
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py::OverheadRatioTests::test_the_ratio_reaches_the_velocity_record
- **Verified:** yes (2026-07-28)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-28 | sdlc-studio | Created via `new` (deterministic) |
| 2026-07-28 | Claude Fable 5 | Groomed against the carried lessons |
