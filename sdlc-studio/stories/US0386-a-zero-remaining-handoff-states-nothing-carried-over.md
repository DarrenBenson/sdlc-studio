# US0386: a zero-remaining handoff states nothing carried over, non-zero unchanged, two-sided tests

> **Status:** Done
> **Delivers:** CR0386
> **Created:** 2026-07-23
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Epic:** EP0142
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_handoff_line.py

## User Story

**As a** operator running sprint plan after a clean close
**I want** the handoff line to say nothing carried over when there is nothing outstanding
**So that** a clean handoff reads as good news rather than a false action item above the warnings that need reading

## Acceptance Criteria

### AC1: a zero-remaining handoff states nothing carried over

- **Given** the last run closed with 0 remaining items
- **When** sprint plan prints the handoff line
- **Then** it states that nothing carried over and offers no `--worklist` command
- **Verify:** manual - retired by US0967: the close and `sprint.py sign` write no handoff, so the close's handoff step, the plan's handoff notice and their tests were deleted; the next `sprint plan` reads the last signed report's handed-over items
- **Verified:** manual (2026-10-01) - retired, superseded by US0967

### AC2: a non-zero handoff is unchanged

- **Given** the last run left 1 or more remaining items
- **When** sprint plan prints the handoff line
- **Then** the existing line is unchanged, naming the count and the worklist path
- **Verify:** manual - retired by US0967: the close and `sprint.py sign` write no handoff, so the close's handoff step, the plan's handoff notice and their tests were deleted; the next `sprint plan` reads the last signed report's handed-over items
- **Verified:** manual (2026-10-01) - retired, superseded by US0967

### AC3: the boundary is pinned two-sided

- **Given** the boundary between zero and one remaining item
- **When** the tests run
- **Then** both the zero-case suppression and the non-zero retention are asserted in one test, so a future change cannot make the zero case reappear or suppress the non-zero one
- **Verify:** manual - retired by US0967: the close and `sprint.py sign` write no handoff, so the close's handoff step, the plan's handoff notice and their tests were deleted; the next `sprint plan` reads the last signed report's handed-over items
- **Verified:** manual (2026-10-01) - retired, superseded by US0967

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-23 | sdlc-studio | Created via `new` (deterministic) |
