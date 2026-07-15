# US0151: hint surfaces the Discovery backlog: how many items await refinement or triage

> **Status:** Done
> **Created:** 2026-07-15
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/status.py
> **Epic:** EP0041
> **Points:** 3

## User Story

**As an** operator
**I want** the hint to name how many Discovery items await refinement/triage
**So that** the dual-track is visible from the first command I reach for.

## Acceptance Criteria

### AC1: hint carries and prints the Discovery-awaiting count, excluding decomposed/terminal items

- **Given** a mix of decomposed and undecomposed Discovery items
- **When** `status hint` runs
- **Then** `discovery_awaiting` counts only the non-terminal, childless Discovery items, the hint result carries it, and the hint prints "discovery: N item(s) await refinement/triage"
- **Verify:** shell cd .claude/skills/sdlc-studio/scripts && python3 -m unittest tests.test_two_backlogs.DiscoverySurfacingTests.test_discovery_awaiting_excludes_decomposed_and_terminal tests.test_two_backlogs.DiscoverySurfacingTests.test_hint_carries_discovery_and_prints_it
- **Verified:** yes (2026-07-16)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-15 | sdlc-studio | Created via `new` (deterministic) |
