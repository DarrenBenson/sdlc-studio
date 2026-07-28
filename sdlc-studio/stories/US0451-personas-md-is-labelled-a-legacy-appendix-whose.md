# US0451: personas.md is labelled a legacy appendix whose still-true content is folded into or pointed at the registry

> **Status:** Done
> **Delivers:** CR0426
> **Created:** 2026-07-27
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** sdlc-studio/personas.md, sdlc-studio/personas/index.md, tools/tests/test_persona_coherence.py
> **Epic:** EP0166
> **Points:** 2

## User Story

**As a** reader who lands on `personas.md` expecting the current design target
**I want** it labelled a legacy appendix that points at the registry
**So that** nobody designs against a superseded persona set that still reads as authoritative

## Acceptance Criteria

### AC1: personas.md declares itself superseded and points at the registry

- **Given** the demoted `personas.md`
- **When** it is opened
- **Then** its opening declares it a legacy appendix superseded by `sdlc-studio/personas/index.md`, with that pointer ahead of any persona content, and any still-true content is folded into the registry or explicitly marked historical
- **Verify:** pytest tools/tests/test_persona_coherence.py::LegacyAppendixTests::test_personas_md_declares_itself_superseded_by_the_registry
- **Verified:** yes (2026-07-27)

### AC2: no live document routes a reader to the superseded set

- **Given** every tracked markdown file, discovered by listing them rather than from a hand-written list
- **When** they are scanned for references to `personas.md`
- **Then** each remaining reference is either inside `personas.md` itself or explicitly labelled legacy, so no live document sends a reader to the superseded personas
- **Verify:** pytest tools/tests/test_persona_coherence.py::LegacyAppendixTests::test_no_live_document_routes_to_the_superseded_set
- **Verified:** yes (2026-07-27)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-27 | sdlc-studio | Created via `new` (deterministic) |
| 2026-07-27 | Claude Fable 5 | Groomed: user story and acceptance criteria authored against the slice |
