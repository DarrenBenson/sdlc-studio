# EP0028: Era completion and DX: v3 identity everywhere, conventions consistent

> **Status:** Done
> **Created:** 2026-07-10
> **Created-by:** sdlc-studio new

## Summary

v3 identity must hold everywhere without the single-writer convention before
multi-agent waves become the normal mode, and the conventions agents script against (exit codes,
json parity, CLI grammar, artefact types) must be uniform. Closes the era RFC0024 opened and the
DX debt RV0007 catalogued. Runs third, pre-tag; clearing it empties the backlog and unlocks v4.

## Story Breakdown

Unit roster (bugs fixed directly; CRs decompose via `cr action` at execution - stories land under this epic):

- [x] [BG0099](../bugs/BG0099-artifact-new-batch-cannot-link-a-story-to.md) - v3 ULID epic cannot be linked from a new story (greenfield flow broken on default schema)
- [x] [BG0086](../bugs/BG0086-v3-short-ids-carry-zero-randomness-uncoordinated-writers.md) - v3 short ids carry zero randomness: same-second writers collide
- [x] [BG0087](../bugs/BG0087-migrate-v3-id-minting-wraps-at-1024-files.md) - migrate_v3 counter wraps at 1024 (silent overwrite) + slug pollution
- [x] [BG0088](../bugs/BG0088-format-json-suppresses-failure-exit-codes-on-reconcile.md) - --format json suppresses failure exits (apply/report; fields drift-blind)
- [x] [BG0093](../bugs/BG0093-config-failure-handling-remains-three-regime-post-cr0180.md) - config failure handling: three regimes -> one warn-and-default contract
- [x] [BG0097](../bugs/BG0097-the-finding-filer-emits-markdownlint-breaking-artefacts-when.md) - finding filer emits markdownlint-breaking artefacts (self-demonstrated)
- [x] [CR0208](../change-requests/CR0208-quality-and-docs-debt-low-themed-duplication-conventions.md) - quality and docs debt themed: duplication, conventions, doc accuracy, DX (20 items)
- [x] [CR0210](../change-requests/CR0210-consistent-cli-argument-grammar-across-the-script-family.md) - consistent CLI argument grammar across the script family
- [x] [CR0211](../change-requests/CR0211-retros-and-reviews-become-first-class-artifact-types.md) - retros and reviews become first-class artifact types

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-10 | sdlc | Created via `new` (deterministic) |
