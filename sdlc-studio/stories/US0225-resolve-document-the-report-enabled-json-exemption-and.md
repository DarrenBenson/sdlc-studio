# US0225: resolve/document the report.enabled json exemption and test the json path

> **Status:** Done
> **Created:** 2026-07-17
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint_report.py, .claude/skills/sdlc-studio/reference-scripts-domain.md
> **Epic:** EP0074
> **Points:** 2

## User Story

**As a** maintainer of a project that turned report rendering off
**I want** the `--format json` exemption stated and tested
**So that** I know whether data is still reachable, instead of discovering it by reading the source

## Acceptance Criteria

### AC1: State the page-versus-data gate where the code claims otherwise

- **Given** `report.enabled: false` suppresses only the text page while `--format json` still returns the whole composed report, and the printed notice says rendering is disabled outright
- **When** a maintainer reads `rendering_enabled`, the gate in `cmd_show` and the notice it prints
- **Then** all three say the same thing: the text page is not drawn, json data remains available, and measurement is never gated
- **Verify:** grep "json data remains available" .claude/skills/sdlc-studio/scripts/sprint_report.py
- **Verified:** yes (2026-07-19)

### AC2: Test the json path against a disabled config

- **Given** a project root whose config sets `report.enabled: false`
- **When** `cmd_show` runs with `--format json`
- **Then** a named test asserts the composed report is printed as json with no disabled notice, and the exit code is 0
- **Verify:** shell cd .claude/skills/sdlc-studio/scripts && python3 -m unittest tests.test_sprint_report.ConfigGateJsonTests
- **Verified:** yes (2026-07-19)

### AC3: Correct the scripts catalogue entry

- **Given** `reference-scripts-domain.md` describes `report.enabled` as an unconditional gate and names no command surface
- **When** a reader uses that entry to decide what the switch does and how to run the report
- **Then** it scopes the gate to the text page, records that json data stays available, and cross-references the sprint command route
- **Verify:** grep "/sdlc-studio sprint report" .claude/skills/sdlc-studio/reference-scripts-domain.md
- **Verified:** yes (2026-07-19)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-17 | sdlc-studio | Created via `new` (deterministic) |
