# BG0395: The in-flight lane warning fires only for a unit re-briefed in the same command

> **Status:** Fixed
> **Verification depth:** functional (tests red-first)
> **Severity:** Medium
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py
> **Evidence:** adversarial review of RUN-01KYMJEM, reproduced by the reviewer
> **Created:** 2026-07-28
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5; human; v1

## Summary

The stale-marker warning is filtered to units in the current dispatch, so a lane that died on US0001 is never mentioned when the operator briefs US0002 - which is the restart case the marker exists for. Nothing else reads `lanes_in_flight`, and `close_run` leaves markers set.

## Steps to Reproduce

`record_lane_start(US0001)`; `lane brief --units US0002` -> stderr empty.

## Proposed Fix

Warn on every stale marker regardless of the briefed set, and surface them at close.

## Acceptance Criteria

### AC1: a stale marker naming another unit is still reported

- **Given** a lane marked in flight on US0001 while the operator briefs US0002
- **When** it runs
- **Then** the marker is still visible, because that is the restart case the marker exists for and the only one the operator has not already noticed
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::StaleLaneMarkersAreReportedTests::test_a_stale_marker_naming_another_unit_is_still_reported
- **Verified:** yes (2026-07-29)

### AC2: the close reports a unit still marked in flight

- **Given** a run reaching its close with a lane marker still set
- **When** it runs
- **Then** the close names it, so a run cannot be signed off while the tree may carry unattributed work
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::StaleLaneMarkersAreReportedTests::test_the_close_reports_a_unit_still_marked_in_flight
- **Verified:** yes (2026-07-29)

### AC3: a run with no stale marker says nothing

- **Given** a close with every lane returned
- **When** it runs
- **Then** nothing is printed, because a warning on every close is a warning nobody reads
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::StaleLaneMarkersAreReportedTests::test_a_run_with_no_stale_marker_says_nothing
- **Verified:** yes (2026-07-29)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-28 | Claude Opus 5 | Filed |
