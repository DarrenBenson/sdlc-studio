# US0523: The close reports delivery time against overhead time as a ratio, beside the points and token figures

> **Status:** Review
> **Delivers:** CR0462
> **Created:** 2026-07-28
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint_report.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py
> **Epic:** EP0179
> **Points:** 5
> **Persona:** Maya Okafor

## User Story

**As a** operator deciding whether the discipline is worth its cost
**I want** the close to report delivery time against overhead time as a ratio
**So that** the number that tests the product's central claim is recorded rather than worked out by hand after somebody complains

## Acceptance Criteria

### AC1: the close reports the ratio beside the points and token figures

- **Given** a closed run with recorded timings
- **When** the close reports
- **Then** it states delivery time, overhead time and the ratio between them, alongside the figures it already carries
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py::OverheadRatioTests::test_the_close_reports_the_ratio
- **Verified:** yes (2026-07-28)

### AC2: the components are derived from what the run recorded, not estimated at close

- **Given** a run whose gate, review and repair timings were recorded
- **When** the ratio is computed
- **Then** each component comes from the run's own record rather than from a figure invented at close time
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py::OverheadRatioTests::test_the_components_are_derived_not_estimated
- **Verified:** yes (2026-07-28)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-28 | sdlc-studio | Created via `new` (deterministic) |
| 2026-07-28 | Claude Fable 5 | Groomed against the carried lessons |
