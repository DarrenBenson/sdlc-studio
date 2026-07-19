# US0235: reference-sprint documentation and tests for the rolling policy

> **Status:** Done
> **Created:** 2026-07-17
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/reference-sprint.md
> **Epic:** EP0076
> **Points:** 2

## User Story

**As an** agent onboarding to the sprint loop
**I want** the rolling policy documented in the sprint reference and covered end to end
**So that** the boundary sequence is discoverable from the docs and proven by a test rather than inferred from the code

## Acceptance Criteria

### AC1: Document the rolling policy in the sprint reference

- **Given** `reference-sprint.md`
- **When** a reader looks for how to run several cycles unattended
- **Then** a "Rolling multi-sprint policy" section documents the standing-policy flags, the boundary sequence (close-down, fetch, regenerate, preview), the three stop causes, and that the whole thing is opt-in
- **Verify:** grep "Rolling multi-sprint policy" .claude/skills/sdlc-studio/reference-sprint.md
- **Verified:** yes (2026-07-19)

### AC2: Cover the boundary sequence end to end

- **Given** a fixture repo with a backlog big enough for two cycles
- **When** a two-cycle rolling run executes against it
- **Then** the test asserts the boundary order - close-down, then fetch, then regenerate, then preview - and that both cycles left their own records
- **Verify:** shell python3 -m unittest discover -s .claude/skills/sdlc-studio/scripts/tests -p test_sprint_rolling.py -k RollingEndToEndTests
- **Verified:** yes (2026-07-19)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-17 | sdlc-studio | Created via `new` (deterministic) |
