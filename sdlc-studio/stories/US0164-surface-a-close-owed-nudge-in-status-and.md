# US0164: Surface a close-owed nudge in status and hint

> **Status:** Done
> **Created:** 2026-07-16
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/status.py
> **Epic:** EP0046
> **Points:** 3

## User Story

**As an** operator who checks status between sprints
**I want** a soft advisory when a sprint close is owed
**So that** I see a skipped close-down where I already look, not sprints later

## Acceptance Criteria

### AC1: status and hint carry a close-owed advisory only when a close is genuinely owed

- **Given** a baselined project with a delivery unit terminal since the baseline and no covering retro
- **When** `status hint` or `status pillars` runs
- **Then** an `advisory:` line names the owed units and points at the retro/`--require-retro` remedy;
  an unbaselined project, or one whose owed work is all grandfathered or retro-covered, stays silent
- **Verify:** shell python3 -m unittest discover -s .claude/skills/sdlc-studio/scripts/tests -p test_status.py
- **Verified:** yes (2026-07-16)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-16 | sdlc-studio | Created via `new` (deterministic) |
