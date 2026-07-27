# US0446: Accept transition set ID Status positionally, or name the exact fix in the error

> **Status:** Review
> **Delivers:** CR0423
> **Created:** 2026-07-27
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/transition.py,.claude/skills/sdlc-studio/scripts/tests/test_transition.py
> **Epic:** EP0165
> **Points:** 2

## User Story

**As a** {{role}}
**I want** {{capability}}
**So that** {{benefit}}

## Acceptance Criteria

### AC1: the natural positional form is accepted

- **Given** the gated status-change tool
- **When** it is invoked as `transition.py set <ID> <STATUS>` (the obvious first attempt)
- **Then** it transitions that id to that status, exactly as `set --id <ID> --status <STATUS>` does
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_transition.py::PositionalSetFormTests::test_positional_set_form_transitions
- **Verified:** yes (2026-07-27)

### AC2: mixing the positional and flag form for the same value is refused clearly

- **Given** an invocation giving the id (or status) both positionally and via a flag
- **When** it runs
- **Then** it refuses with an error naming the correct form, rather than silently picking one
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_transition.py::PositionalSetFormTests::test_positional_and_flag_conflict_refused
- **Verified:** yes (2026-07-27)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-27 | sdlc-studio | Created via `new` (deterministic) |
