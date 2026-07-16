# CR-0240: Document the retro: help/retro.md and reference-retro.md

> **Status:** Complete
> **Size:** S
> **Created:** 2026-07-14
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Priority:** P2
> **Type:** docs

## Summary

gate.py has a blocking retro leg - a sprint close cannot report success without its batch retro - but there is no help/retro.md and no reference-retro.md anywhere in the skill. The one ceremony the gate enforces is the one ceremony we never documented, so what belongs in a retro, and what a finding is supposed to become, is folklore carried in the heads of whoever wrote the last 23. Document the artefact, its sections, and (once RFC0032 lands) the disposition rule that a finding must be filed or declined.

## Impact

A gate that blocks on an undocumented artefact teaches the agent to satisfy the check rather than do the work.

**Effort:** S

## Acceptance Criteria

- [ ] **AC1:** `help/retro.md` exists and documents the retro command surface, the sections a
      retro must carry, and what a finding is.
- [ ] **AC2:** `reference-retro.md` exists and documents the workflow, including how a finding is
      dispositioned (filed as a Bug/CR, or declined with a recorded reason).
- [ ] **AC3:** Both files are reachable from the router, so they are discoverable rather than
      orphaned: `help/references.md` and `help/help.md` link them, and an agent that asks for
      retro help is routed to them without knowing the filenames.
- [ ] **AC4:** An agent that trips the blocking `--require-retro` leg is told, in the failure
      message, where the rules live - it names the doc rather than leaving the agent to guess.
- [ ] **AC5:** The full gate stays green with the new docs in place.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-14 | sdlc-studio | Created via `new` (deterministic) |
