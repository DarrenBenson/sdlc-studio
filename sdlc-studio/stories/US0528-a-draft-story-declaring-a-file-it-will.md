# US0528: A Draft story declaring a file it will create is not warned as unresolvable, since that is the normal case

> **Status:** Ready
> **Delivers:** CR0456
> **Created:** 2026-07-28
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/validate.py, .claude/skills/sdlc-studio/scripts/tests/test_validate.py
> **Epic:** EP0180
> **Points:** 2
> **Persona:** Maya Okafor

## User Story

**As a** author of a Draft story that declares a file it will create
**I want** the unresolvable-path warning not to fire on the normal case
**So that** the warning means something when it does fire

## Acceptance Criteria

### AC1: a Draft story declaring a file it will create is not warned

- **Given** a Draft story whose Affects names a file that does not exist yet
- **When** validate runs
- **Then** no unresolvable warning is raised, because declaring what you will create is the normal case for new work
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_validate.py::ScopedCheckTests::test_a_draft_declaring_a_new_file_is_not_warned

### AC2: a terminal unit naming a path that never existed is still warned

- **Given** a terminal unit whose Affects names a path absent from the tree
- **When** validate runs
- **Then** the warning is raised, because at that point the file should exist and its absence is a real signal
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_validate.py::ScopedCheckTests::test_a_terminal_unit_with_a_missing_path_is_still_warned

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-28 | sdlc-studio | Created via `new` (deterministic) |
| 2026-07-28 | Claude Fable 5 | Groomed against the carried lessons |
