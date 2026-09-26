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
- **Verify:** manual - retired by US0940: US0832 AC5 made PREPARE print exactly one account of the run, the filed report, so the close no longer draws a report page before a brief; pinned by `test_sprint.py::PrepareAndSealTests::test_prepare_prints_exactly_one_account_of_the_run`
- **Verified:** manual (2026-09-26) - retired, superseded by US0832

### AC2: `report.enabled: false` skips the page, never the close

- **Given** a project whose `.config.yaml` sets `report.enabled: false`
- **When** the same close runs
- **Then** the report page is omitted, the chain still completes, the brief still prints, and the exit code is the same as with rendering on
- **Verify:** manual - retired by US0940: US0832 AC5 removed the drawn page from the close, so `report.enabled` gates no close step; the switch still gates `sprint_report` rendering (`test_sprint_report.py`)
- **Verified:** manual (2026-09-26) - retired, superseded by US0832

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
| 2026-09-26 | US0940 | AC1 and AC2 retired in the D0259 pattern: US0832 (9ea7e162) deleted CloseDrawsReportTests and CloseReportDisabledTests with the drawn page, without retiring these stamps |
