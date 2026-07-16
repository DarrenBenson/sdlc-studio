# CR-0309: refine seeds each minted story's ACs from the request's acceptance criteria instead of leaving {{placeholder}} scaffolds

> **Status:** Complete
> **Decomposed-into:** EP0057
> **Priority:** Medium
> **Type:** Improvement
> **Size:** S
> **Affects:** .claude/skills/sdlc-studio/scripts/refine.py, .claude/skills/sdlc-studio/scripts/artifact.py
> **Date:** 2026-07-16
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Fable 5; agent; dogfood retro 2026-07-16

## Summary

refine apply takes 'title|points|affects' per story and mints template-scaffold stories; the request's Acceptance Criteria section (mandatory on every CR the filer accepts) is not carried over. Observed 2026-07-16 delivering CR0283/0292/0297: each CR carried exact, checkable ACs, and each minted story (US0177-US0179) arrived as pure {{placeholder}} boilerplate to be hand-filled with essentially those same ACs. A deterministic copy - each request AC becomes a story AC block with Given/When/Then left to the author and 'Verify: {{executable check}}' placeholder - preserves the judgement boundary (the agent still writes the executable proof) while removing the transcription. Single-story refines get all ACs; multi-story refines could accept an AC-to-story mapping or default to copying the list into the first story for redistribution.

## Impact

Every refine currently mints stories whose whole body is {{role}}/{{capability}}/{{define}} scaffold, so the agent hand-writes ACs the request already states - re-derivation the deterministic layer could do.

## Acceptance Criteria

- [ ] refine apply copies the request's '- [ ]' acceptance criteria into the minted story/stories as AC sections (title from the criterion text, Verify left as placeholder)
- [ ] A flag (e.g. --no-seed-acs) restores the bare-scaffold behaviour
- [ ] validate/critic still flag the story until the seeded Verify placeholders are made executable - seeding must not fake readiness

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-16 | Claude Fable 5 | Raised |
