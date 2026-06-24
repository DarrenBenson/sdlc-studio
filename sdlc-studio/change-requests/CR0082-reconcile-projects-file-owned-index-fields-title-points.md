# CR-0082: reconcile projects file-owned index fields (title, points, persona) not just status and counts

> **Status:** Complete
> **Created:** 2026-06-24
> **Created-by:** sdlc-studio new
> **Priority:** Medium
> **Type:** Improvement

## Summary

The story index template carries per-row fields the **file** owns - `Title`, `Points`,
`Persona`, `Owner` (see `templates/indexes/story.md`, both the per-epic and All-Stories
tables). But `reconcile` projects only **status** (file vs index row) and the **summary
counts**. So those file-owned cells must be populated by hand. A greenfield agent audited
33 generated stories and found structure held perfectly - the *only* thing it had to
centrally reconcile was **story points**, which it had to `grep` back out of all 33 files
and hand-copy into the index. Make `reconcile` project the file-owned per-row fields too,
so the index is fully derived (LL0001: file is truth, the index is derived).

## Problem

From a greenfield agent's audit of 33 real story files (verbatim): *"The ONE thing I had
to centrally reconcile was story points - I had to grep them back out of all 33 files to
populate the index, because each agent assigned its own... agent-owned content came out
uniform; the only residual cost was a structured field feeding the index - exactly the
wiring a deterministic tool should own."*

The audit is the evidence: identical heading signatures across all 33, 33/33 header
fields, 1:1 AC-to-Verify parity, every persona anchor resolving, the rollback flags
exactly right. Structure did not drift. The residual coordination cost was 100% a
file-owned structured field (`Points`) that the index displays but `reconcile` does not
sync - and the same applies to `Title` (the H1 can be edited after creation) and
`Persona`. `reconcile` already treats the index as derived for status and counts (LL0001,
CR0026); this extends that to the remaining derived cells.

## Proposed Changes

### Item 1: Project file-owned per-row fields in reconcile

**Priority:** Medium
**Effort:** 2

Extend `reconcile` (detect + apply) so a story index row's `Title`, `Points`, and
`Persona` cells are read from the backing file (the H1, the `**Story Points:**` field,
the persona reference) and synced when they drift - the same detect/apply discipline that
already governs status. Read-only `detect` reports the drift; `apply` fixes it behind
`--dry-run`. Generalise positionally so epic index rows benefit too where they carry
file-owned cells.

### Item 2: Guard against clobbering judgement cells

**Priority:** Medium
**Effort:** 1

Only project cells whose source-of-truth is unambiguous in the file (BG0032 lesson - never
guess a cell and risk clobbering a title). Where a field is absent in the file (e.g. points
not yet assigned), leave the cell as `-`/for-refinement rather than blanking a value an
operator set. Document which cells are file-derived vs index-only.

## Acceptance Criteria

- [x] `reconcile fields` reports drift between a story file's H1 / `Story Points` and the
      matching index cells (persona **deferred** - no single canonical field in a story; it
      lives in prose, so projecting it would risk the BG0032 clobber class)
- [x] `reconcile fields --apply` syncs those cells from the file (default reports), by the
      same discipline as status (no positional clobbering, BG0032; rows round-trip-verified)
- [x] a file with no `Story Points` field leaves the index cell untouched (`-`), never
      blanked
- [x] after a batch story create + content fill, a single `reconcile apply` populates the
      `Points` column with zero hand-copying (the audited friction is closed)
- [x] unit tests cover: title drift, points projection, absent-points safety; CHANGELOG
      `[Unreleased]` entry same commit (LL0004)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-06-24 | sdlc | Created via `new` (deterministic) |
| 2026-06-24 | sdlc | Scope note from a live tranche: `transition.py` already *preserves* points/title/persona cells on a status cascade (no clobber, a confirmed win). The remaining gap this CR covers is the initial **projection** of file-owned fields into the index and **drift-sync** when the file changes - not the status-cascade hold |
| 2026-06-24 | sdlc | Delivered as `reconcile fields [--apply]` (a dedicated subcommand, kept separate from the tested status `apply` to limit blast radius). Title + Points projected; persona deferred (no canonical file field). Rows round-trip-verified before rewrite (BG0032) |
