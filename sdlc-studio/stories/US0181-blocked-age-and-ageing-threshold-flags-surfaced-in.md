# US0181: Blocked-age and ageing-threshold flags surfaced in status

> **Status:** Draft
> **Created:** 2026-07-16
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/flow.py, .claude/skills/sdlc-studio/scripts/status.py, .claude/skills/sdlc-studio/scripts/tests/test_flow.py
> **Epic:** EP0052
> **Depends on:** US0180
> **Points:** 2

## User Story

**As** Maya Okafor (solo founder-engineer, the Primary)
**I want** blocked-age and an ageing flag surfaced where I already look (status)
**So that** a unit quietly stuck In Progress or Blocked becomes visible before it rots

## Acceptance Criteria

### AC1: Blocked units report blocked-age separately

- **Given** a unit whose Status is Blocked
- **When** flow compute runs
- **Then** its blocked-age (days since the Blocked transition) is reported distinctly from its total age
- **Verify:** shell python3 -m unittest discover -s .claude/skills/sdlc-studio/scripts/tests/ -p test_flow.py -k BlockedAge

### AC2: Ageing threshold flags in status

- **Given** an In Progress unit older than the configured ageing threshold (flow.ageing_days)
- **When** status runs
- **Then** the unit is flagged with its age; under the threshold, or with no config, nothing is flagged
- **Verify:** shell python3 -m unittest discover -s .claude/skills/sdlc-studio/scripts/tests/ -p test_flow.py -k AgeingFlag

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-16 | sdlc-studio | Created via `new` (deterministic) |
