# US0176: Report rendering gated by config while measurement is always recorded

> **Status:** Done
> **Created:** 2026-07-16
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint_report.py
> **Epic:** EP0048
> **Points:** 2

## User Story

**As a** token-conscious project
**I want** to turn the report page off without turning measurement off
**So that** I save render cost while the estimator stays falsifiable

## Acceptance Criteria

### AC1: report.enabled=false disables rendering only; measurement is untouched; default is enabled

- **Given** a project with `report.enabled: false`, and one with the default
- **When** `sprint_report show` runs
- **Then** the disabled project prints a rendering-disabled notice (stating telemetry is unaffected) and the default renders the report
- **Verify:** shell python3 -m unittest discover -s .claude/skills/sdlc-studio/scripts/tests -p test_sprint_report.py -k ConfigGate
- **Verified:** yes (2026-07-16)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-16 | sdlc-studio | Created via `new` (deterministic) |
