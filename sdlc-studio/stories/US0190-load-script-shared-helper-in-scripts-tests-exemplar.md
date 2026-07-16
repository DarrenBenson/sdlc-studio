# US0190: load_script shared helper in scripts/tests; exemplar adoption + docstring guidance

> **Status:** Done
> **Created:** 2026-07-16
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/tests/loader.py, .claude/skills/sdlc-studio/scripts/tests/test_flow.py
> **Epic:** EP0060
> **Points:** 1

## User Story

**As** Maya Okafor (solo founder-engineer, the Primary)
**I want** one shared loader for importing a script under test
**So that** the ~40-copy importlib incantation has one authority and a new test module cannot get it wrong

## Acceptance Criteria

### AC1: load_script is the one authority

- **Given** a test module needing a script import
- **When** it calls the shared loader
- **Then** the module loads with sys.modules registration identical to the incantation
- **Verify:** shell python3 -c "import sys; sys.path.insert(0, '.claude/skills/sdlc-studio/scripts/tests'); import loader; assert callable(loader.load_script)"
- **Verified:** yes (2026-07-16)

### AC2: Exemplar + guidance

- **Given** the next test author
- **When** they read the tests package
- **Then** at least one module uses the loader and the docstring names it canonical
- **Verify:** grep "load_script" .claude/skills/sdlc-studio/scripts/tests/test_flow.py
- **Verified:** yes (2026-07-16)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-16 | sdlc-studio | Created via `new` (deterministic) |
