# US0127: G2 derived-terminal gate fires only when enforced

> **Status:** Done
> **Created:** 2026-07-15
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/transition.py
> **Epic:** EP0034
> **Points:** 2

## User Story

**As an** operator on a project that has not opted into the two-backlog workflow
**I want** to complete a CR by assertion as before
**So that** upgrading the skill does not block my existing close flow until I opt in.

## Acceptance Criteria

### AC1: the G2 derived-terminal gate is gated on enforcement

- **Given** an enforced project (a childless CR cannot be Completed) and an unenforced one
- **When** a CR is transitioned to Complete
- **Then** the enforced project derives the terminal from children (blocks a childless/unfinished CR); the unenforced project completes it by assertion, as before
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_two_backlogs.py::DerivedStatusTests
- **Verified:** yes (2026-07-15)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-15 | sdlc-studio | Created via `new` (deterministic) |
