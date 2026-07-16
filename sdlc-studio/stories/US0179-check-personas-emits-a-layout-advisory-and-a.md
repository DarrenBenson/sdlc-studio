# US0179: check_personas emits a layout advisory and a light structural check for personas.md-only projects

> **Status:** Done
> **Created:** 2026-07-16
> **Created-by:** sdlc-studio new
> **Raised-by:** Claude Fable 5; agent; CR0297 delivery
> **Affects:** .claude/skills/sdlc-studio/scripts/validate.py, .claude/skills/sdlc-studio/scripts/tests/test_validate.py
> **Epic:** EP0051
> **Points:** 2

## User Story

**As** an operator validating a project that only has the legacy flat personas.md
**I want** validate to examine the file the story pipeline actually reads
**So that** an empty or boilerplate persona file is flagged instead of passing on a vacuous clean inspection (LL0008)

## Acceptance Criteria

### AC1: A personas.md-only project gets a layout advisory, not a clean pass

- **Given** a project with personas.md and no personas/ registry design cards
- **When** validate's persona check runs
- **Then** a persona-layout advisory names the legacy layout in use
- **Verify:** shell python3 -m unittest discover -s .claude/skills/sdlc-studio/scripts/tests -p test_validate.py -k test_personas_md_only_emits_layout_advisory
- **Verified:** yes (2026-07-16)

### AC2: Empty or template-boilerplate personas.md is flagged

- **Given** a personas.md that is unfilled template or has no persona sections
- **When** the light structural check runs
- **Then** a persona-legacy warning is emitted for each condition
- **Verify:** shell python3 -m unittest discover -s .claude/skills/sdlc-studio/scripts/tests -p test_validate.py -k test_boilerplate_personas_md_flagged -k test_empty_personas_md_flagged -k test_seats_only_registry_falls_back_to_legacy_check
- **Verified:** yes (2026-07-16)

### AC3: The docstring's LL0008 rationale covers the legacy layout explicitly

- **Given** a maintainer reading check_personas
- **When** they check why the legacy layout is examined
- **Then** the docstring states the vacuous-clean-pass rationale for personas.md-only projects
- **Verify:** grep "never a vacuous clean pass on the one persona file actually consumed" .claude/skills/sdlc-studio/scripts/validate.py
- **Verified:** yes (2026-07-16)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-16 | sdlc-studio | Created via `new` (deterministic) |
| 2026-07-16 | Claude Fable 5 | ACs written and delivered (CR0297, TDD: 6 new tests red-then-green) |
