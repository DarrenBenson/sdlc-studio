# US0149: command_audit.py: enumerate every command and route with a keep/fold/retire disposition mapped to the process spine

> **Status:** Done
> **Created:** 2026-07-15
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/command_audit.py
> **Epic:** EP0041
> **Points:** 5

## User Story

**As an** operator planning the command-surface cleanup
**I want** every command enumerated and dispositioned against the process spine
**So that** the cleanup acts on evidence, re-runnable so the surface cannot silently drift.

## Acceptance Criteria

### AC1: command_audit enumerates the surface, maps each command to the spine, and dispositions keep/review

- **Given** the skill command surface (SKILL Type Reference, help catalogue, scripts/)
- **When** `command_audit.audit()` runs
- **Then** every command is placed on the spine (no unmapped on this repo), catalogue drift is flagged both directions, each command gets a keep/review disposition, and `--write` produces `command-audit.md` with a per-spine table
- **Verify:** shell cd .claude/skills/sdlc-studio/scripts && python3 -m unittest tests.test_command_audit.RealRepoAuditTests tests.test_command_audit.FixtureAuditTests.test_drift_both_directions_is_flagged tests.test_command_audit.FixtureAuditTests.test_unmapped_command_is_a_review_candidate tests.test_command_audit.FixtureAuditTests.test_write_produces_the_audit_document
- **Verified:** yes (2026-07-16)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-15 | sdlc-studio | Created via `new` (deterministic) |
