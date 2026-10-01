# BG0824: init guided's personas stage seeds the legacy flat personas.md, which the persona registry and sprint plan --serves never read

> **Status:** Fixed
> **Supersedes:** BG0881
> **Groomed:** 2026-10-01 (D0291) - premise reproduced at HEAD: `init.py guided` to the personas stage leaves `sdlc-studio/personas.md` and no `sdlc-studio/personas/`, while `persona_registry` reads only `personas/index.md`
> **Severity:** Medium
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/init.py, .claude/skills/sdlc-studio/templates/personas/persona-index-template.md, .claude/skills/sdlc-studio/templates/indexes/story.md, .claude/skills/sdlc-studio/help/init.md, .claude/skills/sdlc-studio/scripts/tests/test_lean_guided_personas_seed.py, changelog.d/BG0824.md, .claude/skills/sdlc-studio/scripts/tests/test_init.py
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

Seed `sdlc-studio/personas/index.md` (the registry shape `persona_registry` parses; the shipped persona-index-template has no Primary/Secondary/Negative heading today, so it reads `declares no Primary/Secondary/Negative heading` and needs them) instead of the flat file, point the story index at it, and drop the sequential-numbering note from the index template.

## Acceptance Criteria

- [ ] **AC1** Given a fresh project after `init.py run`, when `init.py guided --root <fixture>` reaches the personas stage, then it seeds `sdlc-studio/personas/index.md` with Primary, Secondary and Negative headings, `sdlc_md.persona_registry(<fixture>)` reads it as available (zero entries until filled), and no `sdlc-studio/personas.md` is created. Fails on: HEAD, which seeds `sdlc-studio/personas.md` and leaves `personas/` absent, so the registry reads `no persona registry at ...`
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_guided_personas_seed.py::GuidedPersonasSeedTests::test_the_registry_is_seeded
- [ ] **AC2** Given the shipped `templates/indexes/story.md`, when `artifact.py batch --type story` renders the story index in a fixture, then its personas link points at `../personas/index.md` and it carries no `US0001, US0002` numbering note. Fails on: HEAD's `[User Personas](../personas.md)` link (line 10) and numbering note (line 40)
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_guided_personas_seed.py::GuidedPersonasSeedTests::test_the_story_index_links_the_registry

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-28 | sdlc-studio | Filed |
