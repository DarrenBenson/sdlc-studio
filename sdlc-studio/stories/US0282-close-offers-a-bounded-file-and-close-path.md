# US0282: Close offers a bounded file-and-close path: blockers filed as linked artefacts, outcome records outstanding work

> **Status:** Done
> **Delivers:** CR0371
> **Created:** 2026-07-20
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/reference-sprint.md
> **Epic:** EP0092
> **Depends on:** US0281
> **Points:** 5

## User Story

**As a** sprint operator
**I want** a close that can file its blockers and close honestly
**So that** a close terminates instead of chasing a moving target

## Acceptance Criteria

### AC1: a blocked close offers a bounded choice

- **Given** a close with unmet blockers
- **When** the close runs
- **Then** the operator is offered fix-them or file-them-and-close, rather than only the fix
  path
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py -k test_blocked_close_offers_file_and_close
- **Verified:** yes (2026-07-20)

### AC2: file-and-close records every blocker as a linked artefact

- **Given** the operator chooses file-and-close
- **When** the close completes
- **Then** each blocker is a real artefact linked to the run, and the run's outcome states
  plainly that it closed with known outstanding work
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py -k test_file_and_close_records_linked_artefacts_and_outcome
- **Verified:** yes (2026-07-20)

### AC3: nothing is silently waived

- **Given** a completed file-and-close
- **When** the retro and the review anchor are read
- **Then** both name what was deferred and why
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py -k test_file_and_close_names_deferrals_in_retro_and_anchor
- **Verified:** yes (2026-07-20)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-20 | sdlc-studio | Created via `new` (deterministic) |
