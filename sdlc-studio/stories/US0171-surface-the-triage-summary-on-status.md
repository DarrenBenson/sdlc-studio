# US0171: Surface the triage summary on status

> **Status:** Done
> **Created:** 2026-07-16
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/status.py
> **Epic:** EP0047
> **Points:** 2

## User Story

**As an** operator checking status
**I want** a backlog-triage summary line
**So that** a dirty backlog is visible on status, not only when plan reads it

## Acceptance Criteria

### AC1: status carries a triage advisory when there are findings, silent on a coherent backlog

- **Given** a backlog with a duplicate pair, then a coherent backlog
- **When** `status.backlog_triage_advisory` runs
- **Then** the first returns an advisory naming the lens counts; the second returns None
- **Verify:** shell python3 -m unittest discover -s .claude/skills/sdlc-studio/scripts/tests -p test_status.py -k BacklogTriage
- **Verified:** yes (2026-07-16)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-16 | sdlc-studio | Created via `new` (deterministic) |
