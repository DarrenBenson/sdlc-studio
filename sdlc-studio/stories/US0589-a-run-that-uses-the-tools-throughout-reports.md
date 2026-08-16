# US0589: A run that uses the tools throughout reports zero manual actions, so the detector cannot be one that never fires

> **Status:** Ready
> **Delivers:** CR0515
> **Created:** 2026-08-01
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py
> **Epic:** EP0196
> **Points:** 2

## User Story

**As a** maintainer trusting the manual-action count
**I want** a run using the tools throughout to report zero
**So that** the detector is measured rather than a label that always fires

## Acceptance Criteria

### AC1: a run using the tools throughout reports zero

- **Given** a run in which every artefact change went through a skill script
- **When** the close composes its report
- **Then** the manual-action count is zero - the control, so the detector cannot be one that never fires or one that always does
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py::ToolUseTests::test_a_clean_run_reports_zero

### AC2: the count moves with the number of hand-edits

- **Given** two runs, one with a single hand-edited artefact and one with three
- **When** each close composes its report
- **Then** the counts are 1 and 3, so the number is measured rather than a label
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py::ToolUseTests::test_the_count_tracks_the_hand_edits

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-01 | sdlc-studio | Created via `new` (deterministic) |
