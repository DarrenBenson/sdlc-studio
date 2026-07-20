# US0275: sprint close runs the preflight before executing any step, so nothing is discovered serially

> **Status:** Done
> **Delivers:** CR0359
> **Created:** 2026-07-20
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py
> **Epic:** EP0089
> **Points:** 2

## User Story

**As a** {{role}}
**I want** {{capability}}
**So that** {{benefit}}

## Acceptance Criteria

### AC1: close runs the pre-flight before executing any step

- **Given** a close with unmet prerequisites
- **When** `sprint.py close` runs
- **Then** the full list is printed before the first chain step executes, so the operator learns
  everything owed up front instead of one blocker per invocation
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py -k test_close_reports_all_blockers_before_executing
- **Verified:** yes (2026-07-20)

### AC2: a close with nothing outstanding is unchanged

- **Given** a workspace where every prerequisite is met
- **When** the close runs
- **Then** it proceeds through the chain exactly as before - the pre-flight adds a report, never
  a new refusal, so no close that previously succeeded now fails
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py -k test_close_with_nothing_outstanding_is_unchanged
- **Verified:** yes (2026-07-20)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-20 | sdlc-studio | Created via `new` (deterministic) |
