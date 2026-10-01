# BG0883: BG0824 did not converge in review: round 2 REJECT findings

> **Status:** Open
> **Severity:** Medium
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/init.py, .claude/skills/sdlc-studio/templates/personas/persona-index-template.md, .claude/skills/sdlc-studio/templates/indexes/story.md, .claude/skills/sdlc-studio/help/init.md, .claude/skills/sdlc-studio/scripts/tests/test_lean_guided_personas_seed.py, changelog.d/BG0824.md, .claude/skills/sdlc-studio/scripts/tests/test_init.py
> **Created:** 2026-10-01
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-10-01T18:14:42Z

## Summary

BG0824 was rejected at round 2, the review cap, by qa-seat reviewer (subagent abf7b661), so it was carried as a known issue rather than reviewed again. The findings still open: [regression] a personas/index.md that is not valid UTF-8 now crashes status and status hint (exit 1) and review\_prep.required\_legs: the new status.personas\_present (status.py:122-134) and review\_prep.py:179 call sdlc\_md.persona\_registry, which catches OSError only (sdlc\_md.py:2666) - reached whenever there is no personas.md and no card, the state guided onboarding leaves - base exits 0 - fix: catch UnicodeDecodeError in persona\_registry; [new] non-blocking: the persona-card branch (status.py:130-131) and review\_prep's entries-not-available check are unpinned

## Steps to Reproduce

1. Read the round 2 REJECT of BG0824 in the verdict ledger.

## Proposed Fix

Fix each finding above, then deliver BG0824 again in a later run.

## Acceptance Criteria

- [ ] **AC1** The round 2 REJECT finding no longer holds: [regression] a personas/index.md that is not valid UTF-8 now crashes status and status hint (exit 1) and review\_prep.required\_legs: the new status.personas\_present (status.py:122-134) and review\_prep.py:179 call sdlc\_md.persona\_registry, which catches OSError only (sdlc\_md.py:2666) - reached whenever there is no personas.md and no card, the state guided onboarding leaves - base exits 0 - fix: catch UnicodeDecodeError in persona\_registry
  - **Verify:** manual - the independent review of the redelivery re-checks this finding
- [ ] **AC2** The round 2 REJECT finding no longer holds: [new] non-blocking: the persona-card branch (status.py:130-131) and review\_prep's entries-not-available check are unpinned
  - **Verify:** manual - the independent review of the redelivery re-checks this finding
- [ ] **AC3** BG0824 AC1 still passes: Given a fresh project after `init.py run`, when `init.py guided --root <fixture>` reaches the personas stage, then it seeds `sdlc-studio/personas/index.md` with Primary, Secondary and Negative headings, `sdlc_md.persona_registry(<fixture>)` reads it as available (zero entries until filled), and no `sdlc-studio/personas.md` is created. Fails on: HEAD, which seeds `sdlc-studio/personas.md` and leaves `personas/` absent, so the registry reads `no persona registry at ...`
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_guided_personas_seed.py::GuidedPersonasSeedTests::test_the_registry_is_seeded
- [ ] **AC4** BG0824 AC2 still passes: Given the shipped `templates/indexes/story.md`, when `artifact.py batch --type story` renders the story index in a fixture, then its personas link points at `../personas/index.md` and it carries no `US0001, US0002` numbering note. Fails on: HEAD's `[User Personas](../personas.md)` link (line 10) and numbering note (line 40)
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_guided_personas_seed.py::GuidedPersonasSeedTests::test_the_story_index_links_the_registry

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-01 | sdlc-studio | Filed |
