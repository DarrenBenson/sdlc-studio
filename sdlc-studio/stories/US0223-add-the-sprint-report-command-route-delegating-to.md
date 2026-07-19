# US0223: add the sprint report command route delegating to sprint_report

> **Status:** Review
> **Created:** 2026-07-17
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/help/sprint.md, .claude/skills/sdlc-studio/SKILL.md
> **Epic:** EP0074
> **Points:** 3

## User Story

**As an** operator closing a sprint
**I want** the sprint report reachable from the sprint command surface
**So that** I can draw it without already knowing `sprint_report.py` exists

## Acceptance Criteria

### AC1: Route `sprint report` to the report composer

- **Given** `sprint_report.py show` composes the end-of-sprint report and `sprint.py` owns the sprint command surface
- **When** an operator runs `sprint.py report --id RETROxxxx`, optionally with `--tokens`, `--elapsed-hours` or `--format json`
- **Then** the same output `sprint_report.py show` would print is produced, every flag is passed through, and the composer's exit code is returned unchanged
- **Verify:** shell cd .claude/skills/sdlc-studio/scripts && python3 -m unittest tests.test_sprint.SprintReportRouteTests
- **Verified:** yes (2026-07-19)

### AC2: Document the route in the sprint help page

- **Given** `help/sprint.md` is what a reader loads for the sprint command and today names no report command
- **When** they read its Quick Reference and See Also
- **Then** `/sdlc-studio sprint report --id RETROxxxx` is listed with a line saying when to run it and what it composes from
- **Verify:** grep "/sdlc-studio sprint report" .claude/skills/sdlc-studio/help/sprint.md
- **Verified:** yes (2026-07-19)

### AC3: List the route in SKILL.md

- **Given** SKILL.md's command table is the router an agent reads before choosing a command
- **When** an agent scans it for a way to report on a finished sprint
- **Then** a row names the report route and points at `help/sprint.md`
- **Verify:** grep "sprint report" .claude/skills/sdlc-studio/SKILL.md
- **Verified:** yes (2026-07-19)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-17 | sdlc-studio | Created via `new` (deterministic) |
