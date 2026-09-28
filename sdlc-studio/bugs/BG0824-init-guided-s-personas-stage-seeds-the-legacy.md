# BG0824: init guided's personas stage seeds the legacy flat personas.md, which the persona registry and sprint plan --serves never read

> **Status:** Open
> **Severity:** Medium
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/init.py, .claude/skills/sdlc-studio/templates/indexes/story.md, .claude/skills/sdlc-studio/help/init.md, .claude/skills/sdlc-studio/scripts/tests/test_lean_guided_personas_seed.py, changelog.d/BG0824.md, .claude/skills/sdlc-studio/scripts/tests/test_init.py
> **Evidence:** v6.0.0-rc.1 soak F4; HEAD 7e53a438 init.py stage_personas seeds `personas`; fixture `artifact.py batch --type story` index shows the ../personas.md link and the US0001 note
> **Created:** 2026-09-28
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-09-28T16:26:23Z

## Summary

`stage_personas` seeds `sdlc-studio/personas.md` from templates/core/personas.md. The skill's own registry calls that file a legacy fallback (reference-story.md:56), and `sdlc_md.persona_registry`, `sprint plan --serves` and the goal trace read `sdlc-studio/personas/index.md` and the cards beside it. A user who fills the seeded file gets no personas where v6 reads them. The story index template repeats the pointer (`Personas Reference: [User Personas](../personas.md)`) and its note still says stories are numbered `US0001, US0002` on a schema v3 project that mints ULIDs.

## Steps to Reproduce

`init.py run`, then `init.py guided` to the personas stage: sdlc-studio/personas.md is seeded; `sprint plan --serves <name>` after filling it finds no persona.

## Proposed Fix

Seed `sdlc-studio/personas/index.md` (the registry shape `persona_registry` parses) instead of the flat file, point the story index at it, and drop the sequential-numbering note from the index template.

## Acceptance Criteria

- [ ] **AC1** Given a fresh project at the guided personas stage, then the file seeded is the registry `persona_registry` reads, and no flat personas.md is created. Fails on: HEAD, which seeds personas.md
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_guided_personas_seed.py::GuidedPersonasSeedTests::test_the_registry_is_seeded
- [ ] **AC2** Given the shipped story index template, then its personas link names the registry and it states no US0001-style numbering. Fails on: HEAD's ../personas.md link and note
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_guided_personas_seed.py::GuidedPersonasSeedTests::test_the_story_index_links_the_registry

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-28 | sdlc-studio | Filed |
