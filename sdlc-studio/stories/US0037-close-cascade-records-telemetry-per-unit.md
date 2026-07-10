# US0037: close cascade records telemetry per unit

> **Status:** Done
> **Created:** 2026-06-21
> **Epic:** EP0008

## User Story

**As a** team running autosprint
**I want** each unit close to record a telemetry event automatically
**So that** run data accrues without manual capture, unblocking calibration (RFC0014 WS2).

## Acceptance Criteria

### AC1: close records a telemetry event (id + type + any metrics), advisory

- **Given** an artifact being closed
- **When** `artifact close --id ... [--iterations --verdict ...]` runs
- **Then** after the transition it records a telemetry entry (id, type, plus passed metrics) to the gitignored state dir, and a telemetry failure never affects the close
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_artifact.py::CloseTests::test_close_records_telemetry_event
- **Verified:** yes (2026-06-21)

## Implementation

`scripts/artifact.py` `close` calls `telemetry.record` after the transition (guarded;
metrics via `--iterations/--verdict/--wall-time-s/--stages`). Documented in
reference-sprint.md. WS3 (calibrate) + WS5 remain deferred.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-06-21 | Autosprint (CR0051) | Created by `new`, closed by `close` - which recorded its OWN telemetry event (meta-dogfood); small guarded wiring over the critic-approved telemetry recorder |
