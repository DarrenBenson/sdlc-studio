# US0152: The main status dashboard shows the Discovery and Delivery split

> **Status:** Done
> **Created:** 2026-07-15
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/status.py
> **Epic:** EP0041
> **Points:** 5

## User Story

**As an** operator
**I want** the main status dashboard to show the Discovery/Delivery split
**So that** the dual-track is visible without running `status backlog`.

## Acceptance Criteria

### AC1: the pillars dashboard and its JSON carry the two-backlog split and the awaiting count

- **Given** a project with Discovery and Delivery items
- **When** `status pillars` runs
- **Then** `gather()` carries `backlogs` (discovery/delivery split + awaiting count) and the text dashboard prints a `Backlogs:` line showing Discovery, awaiting refine/triage, and Delivery
- **Verify:** shell cd .claude/skills/sdlc-studio/scripts && python3 -m unittest tests.test_two_backlogs.DiscoverySurfacingTests.test_dashboard_shows_the_two_backlog_split
- **Verified:** yes (2026-07-16)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-15 | sdlc-studio | Created via `new` (deterministic) |
