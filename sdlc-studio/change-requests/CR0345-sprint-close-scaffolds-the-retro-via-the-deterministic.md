# CR-0345: sprint close scaffolds the retro via the deterministic path instead of requiring a pre-made one

> **Status:** Complete
> **Priority:** Medium
> **Type:** Improvement
> **Size:** S
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py
> **Date:** 2026-07-17
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1

## Summary

Force the retro to go through the tool on close. Today 'sprint close --retro RETROxxxx' REQUIRES the retro to already exist; an agent that hand-authors it (instead of 'artifact.py new --type retro') gets a valid-content file with NO _index.md row, caught only at the reconcile step (6/6) and cleared by a manual 'reconcile apply' (hit live at RETRO0047 close). Make close own the scaffold: --retro becomes optional; omitted -> close runs the deterministic `meta_new` path (allocates id + renders the retro template + adds the index row, pre-filling Batch/Goal from run-state), then STOPS with 'fill it, then re-run close --retro <id>'. --retro given+exists -> proceed, and self-heal a missing index row via `reconcile.apply_meta` so a retro made any other way still cannot stall the close. --retro given+missing -> refuse (a specific id cannot be minted by the allocator; tell them to omit it).

## Impact

Agents closing a sprint. Removes the hand-authored-retro-missing-index-row friction and makes the deterministic scaffold the default path. Backwards-compatible: existing 'close --retro <existing id>' calls behave as before (plus the row self-heal).

## Acceptance Criteria

- [ ] close with --retro OMITTED scaffolds a retro via `meta_new` (id + rendered template + index row), pre-fills Batch/Goal from run-state, prints the re-run command, and STOPS non-zero
- [ ] close with --retro naming an EXISTING retro proceeds as today, and adds the retro's index row if missing (`reconcile.apply_meta)` so it never stalls at the reconcile step
- [ ] close with --retro naming a NON-EXISTENT retro refuses with a message to omit --retro (a specific id cannot be minted by the allocator)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-17 | sdlc-studio | Raised |
