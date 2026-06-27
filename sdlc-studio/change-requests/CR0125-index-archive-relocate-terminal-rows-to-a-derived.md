# CR-0125: index archive: relocate terminal rows to a derived sub-index

> **Status:** Complete
> **Created:** 2026-06-27
> **Created-by:** sdlc-studio new
> **Priority:** Medium
> **Type:** Improvement
> **Affects:** .claude/skills/sdlc-studio/scripts/reconcile.py, .claude/skills/sdlc-studio/scripts/next_id.py, .claude/skills/sdlc-studio/scripts/lib/sdlc_md.py
> **Depends on:** -

## Summary

`_index.md` tables grow monotonically: every artefact that reaches a terminal state keeps a
detail row in the live index forever. On a mature project the live index is almost entirely dead
weight. Measured on a consuming repo (the noted validation repo): `stories/_index.md` is 1740 lines
with 528 of 533 rows terminal (99%); `change-requests/_index.md` 786 lines, 94% terminal;
`bugs/_index.md` 551 lines, 99.7% terminal; `epics/_index.md` 390 lines, 91% terminal. The live
index is loaded routinely (status, browsing, agent pickup), so this is a recurring token cost for
near-zero live signal.

This is progressive disclosure applied to terminal rows, and it is the right mechanism rather than
relocating the artefact **files** (the plan-mode `archive` model): the files never move, so no link
churn, no path re-homing, and the file census is untouched. Only the **derived** index gets tiered.

The read path is already built. `reconcile.parse_index` (reconcile.py:225-247) UNIONS the live
`_index.md` rows with any rows found in `<type>/archive/**/*.md` sub-indexes, so a row relocated out
of the live table is still seen as "in the index" (no false missing-row) and the census stays
correct ([[LL0001]] - census is the authority, the index is derived). What is missing is the
**writer**: a verb that pulls terminal rows out of the live `_index.md` into a
`<type>/archive/_index-{{period}}.md` sub-index, leaving the live index carrying only active rows
plus the canonical summary count block (which already counts all states).

Two design constraints from the evidence:

1. **Terminal must be vocab-derived, not hardcoded.** Per-project status vocabs differ: stories use
   Done/Won't Implement/Superseded, bugs use Fixed/Closed/Rejected, CRs add Built (treat as
   *active* until Complete). The terminal/absorbing set must come from `status_vocab(type_, root)`
   via a vocab-metadata flag, not a literal list.
2. **`next_id` must union the archive.** `next_id` reads live index rows as a belt-and-braces guard
   against id reuse (next_id.py:74-77). It also scans files, so archived ids stay safe in practice
   (the files do not move), but the id-from-index check must mirror `parse_index`'s archive union so
   the guard is not weakened.

Per [[LL0008]], the writer must fail loud: never drop a row it cannot place, never report a
relocation it did not perform; the live summary total must still equal census after archiving.

## Acceptance Criteria

- [ ] a writer verb relocates rows whose status is terminal (vocab-derived) from the live
      `<type>/_index.md` into `<type>/archive/_index-{{period}}.md`, leaving active rows + the
      canonical summary block in the live index; idempotent (re-running moves nothing new)
- [ ] terminal statuses are read from `status_vocab(type_, root)` via a vocab-metadata flag, not a
      hardcoded list; CR `Built` is classed active, not terminal
- [ ] after archiving, `reconcile detect` reports zero drift: census == unioned index rows, and the
      live summary counts still equal the full census (archived rows still tallied)
- [ ] `next_id` unions `<type>/archive/**/*.md` sub-index rows in its id-from-index guard, mirroring
      `parse_index`, so an archived id is never re-allocated even if its file were removed
- [ ] the writer fails loud per [[LL0008]]: a row it cannot classify or place aborts with a non-zero
      exit and no partial write; no false "archived N rows" report
- [ ] dry-run mode previews the relocation (counts per status, target sub-index path) and writes
      nothing
- [ ] unit tests cover: terminal-vs-active split per vocab, idempotency, reconcile-clean after
      archive, next_id archive-union, fail-loud on unclassifiable row; dry-run against the
      a consuming repo tree shows the expected ~95% live-index reduction with reconcile clean
- [ ] docs: `reference-reconcile.md` + `help/` updated; CHANGELOG `[Unreleased]` entry ([[LL0004]])

## Out of Scope

The monolithic PRD/TRD/TSD documents (a consuming repo: `prd.md` 954KB, `trd.md` 473KB, `tsd.md` 216KB)
are a separate progressive-disclosure problem - section-sharding a single document, not tiering a
derived index. Do not fold it into this CR; it warrants its own RFC so the two mechanisms are not
conflated.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-06-27 | field | Created via `new` (deterministic) |
