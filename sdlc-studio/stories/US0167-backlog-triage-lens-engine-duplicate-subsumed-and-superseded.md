# US0167: Backlog-triage lens engine: duplicate/subsumed and superseded via Affects-overlap and title/summary similarity

> **Status:** Done
> **Created:** 2026-07-16
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/backlog_triage.py
> **Epic:** EP0047
> **Points:** 5

## User Story

**As an** operator about to plan a sprint
**I want** duplicate and subsumed backlog items detected
**So that** I do not plan the same change twice or split one change's ACs across two artefacts

## Acceptance Criteria

### AC1: two open artefacts sharing a file with similar wording are flagged duplicate; a proper Affects subset is flagged subsumed

- **Given** a backlog with a duplicate pair (shared Affects + similar title/summary) and a subsumed pair (one Affects a proper subset of the other)
- **When** `backlog_triage.triage` runs
- **Then** the first is reported `duplicate`, the second `subsumed`, and unrelated items are not flagged
- **Verify:** shell python3 -m unittest discover -s .claude/skills/sdlc-studio/scripts/tests -p test_backlog_triage.py -k Duplicate
- **Verified:** yes (2026-07-16)

### AC2: no shared file or dissimilar wording is not a duplicate

- **Given** two items on different files, or on one file but unrelated wording
- **When** triage runs
- **Then** neither is flagged - the lens does not cry wolf on a clean backlog
- **Verify:** shell python3 -m unittest discover -s .claude/skills/sdlc-studio/scripts/tests -p test_backlog_triage.py -k Duplicate
- **Verified:** yes (2026-07-16)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-16 | sdlc-studio | Created via `new` (deterministic) |
