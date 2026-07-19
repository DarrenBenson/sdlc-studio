# US0224: draw the report in the close ceremony when report.enabled

> **Status:** Done
> **Created:** 2026-07-17
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/reference-sprint.md
> **Epic:** EP0074
> **Points:** 2

## User Story

**As an** operator running the close ceremony
**I want** the sprint report drawn as part of the close
**So that** what the sprint delivered and cost is on the page I sign off, not a command I must remember

## Acceptance Criteria

### AC1: The close chain draws the report

- **Given** a run with a filled retro whose close chain completes, in a project that has not turned rendering off
- **When** `sprint.py close --retro RETROxxxx` finishes its chain
- **Then** the composed sprint report is printed before the sign-off decision brief, and a report that cannot be composed is noted without failing the close
- **Verify:** shell cd .claude/skills/sdlc-studio/scripts && python3 -m unittest tests.test_sprint.CloseDrawsReportTests
- **Verified:** yes (2026-07-19)

### AC2: `report.enabled: false` skips the page, never the close

- **Given** a project whose `.config.yaml` sets `report.enabled: false`
- **When** the same close runs
- **Then** the report page is omitted, the chain still completes, the brief still prints, and the exit code is the same as with rendering on
- **Verify:** shell cd .claude/skills/sdlc-studio/scripts && python3 -m unittest tests.test_sprint.CloseReportDisabledTests
- **Verified:** yes (2026-07-19)

### AC3: Document the report step in the close ceremony

- **Given** `reference-sprint.md` describes the close chain step by step and mentions no report step
- **When** a reader follows that description
- **Then** it says the close draws the sprint report, where in the chain, and that `report.enabled` gates only the drawing
- **Verify:** grep "draws the sprint report" .claude/skills/sdlc-studio/reference-sprint.md
- **Verified:** yes (2026-07-19)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-17 | sdlc-studio | Created via `new` (deterministic) |
