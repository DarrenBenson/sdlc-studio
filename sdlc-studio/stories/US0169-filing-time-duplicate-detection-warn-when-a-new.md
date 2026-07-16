# US0169: Filing-time duplicate detection: warn when a new finding overlaps an open artefact

> **Status:** Done
> **Created:** 2026-07-16
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/file_finding.py
> **Epic:** EP0047
> **Points:** 3

## User Story

**As an** agent filing findings at speed
**I want** a warning when a new finding overlaps an open artefact
**So that** near-duplicates are caught at the cheapest moment, before the id is minted

## Acceptance Criteria

### AC1: a near-duplicate finding is warned (candidate named) but still filed; a distinct finding is not warned

- **Given** an open artefact, and a new finding that shares its Affects and wording
- **When** `file_finding` files the new finding
- **Then** the result carries `duplicate_warnings` naming the candidate, and the finding is still filed (never refused); a finding on a different file with different words carries no warning
- **Verify:** shell python3 -m unittest discover -s .claude/skills/sdlc-studio/scripts/tests -p test_file_finding.py -k FilingTime
- **Verified:** yes (2026-07-16)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-16 | sdlc-studio | Created via `new` (deterministic) |
