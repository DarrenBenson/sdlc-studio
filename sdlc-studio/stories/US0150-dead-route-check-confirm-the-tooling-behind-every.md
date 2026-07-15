# US0150: Dead-route check: confirm the tooling behind every kept command runs

> **Status:** Done
> **Created:** 2026-07-15
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/command_audit.py
> **Epic:** EP0041
> **Points:** 3

## User Story

**As an** operator
**I want** the tooling behind every command confirmed to run
**So that** no help entry points at a dead or broken script.

## Acceptance Criteria

### AC1: --check-tools detects a broken tool and a good one; --strict exits non-zero on a broken tool

- **Given** a skill fixture with a good and a broken script
- **When** `command_audit` runs with `--check-tools` (and `--strict`)
- **Then** the good script is alive, the broken one is flagged, the summary counts the broken tool, and `--strict` exits non-zero
- **Verify:** shell cd .claude/skills/sdlc-studio/scripts && python3 -m unittest tests.test_command_audit.FixtureAuditTests.test_broken_tool_detected_and_good_tool_alive tests.test_command_audit.FixtureAuditTests.test_strict_exit_nonzero_on_broken_tool
- **Verified:** yes (2026-07-16)

### AC2: the real repo's tooling is all alive

- **Given** this repo's 61 scripts
- **When** `command_audit --check-tools` runs
- **Then** zero broken tools are reported
- **Verify:** shell python3 .claude/skills/sdlc-studio/scripts/command_audit.py --check-tools --strict >/dev/null
- **Verified:** yes (2026-07-16)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-15 | sdlc-studio | Created via `new` (deterministic) |
