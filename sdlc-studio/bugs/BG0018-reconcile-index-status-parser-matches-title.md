# BG-0018: reconcile index-status parser matches a status word in the title column

> **Status:** Open
> **Severity:** Medium
> **Reporter:** Autosprint (determinism-sprint)
> **Date:** 2026-06-20
> **Epic:** --
> **Story:** --

## Summary

`reconcile detect` reads a story's index-row status by canonical-status-matching
across the row's cells rather than the positional Status column, so a row whose
**title** begins with a status vocabulary word is misclassified. US0014, titled
"review_prep staleness determinism", had its index status read as **Review**
(file status was correctly Done), producing a spurious `status-mismatch` plus a
cascading `count-mismatch`.

## Steps to Reproduce

1. Add a story to `stories/_index.md` whose title column starts with a status
   word, e.g. `| [US0014](...) | review_prep staleness determinism | Done | ... |`.
2. Run `reconcile.py detect --scope stories`.
3. Observe `status-mismatch US0014: index_status 'Review'` though the row's Status
   column is `Done`.

## Expected

The index-row status is read from the Status **column** (positional), so the title
text never influences it.

## Actual

`canonical_status` matches "review_prep..." (prefix "review") to the vocab term
`Review` from a non-status cell, before the real Status column is consulted.

## Workaround

Retitled the US0014 index row to "Staleness determinism for review_prep" (does not
lead with a status word). The underlying parser fragility remains.

## Proposed Fix

Parse the index row by column position (the documented index schema) for the
Status field, instead of scanning all cells for the first canonical-status match.
Add a regression test: a story titled "Review the login flow" with Status Done is
read as Done, not Review.

**Scope (systemic).** The root cause is `sdlc_md.canonical_status` prefix-matching
(a vocab term followed by a non-alphanumeric boundary), which is correct for a
real status field (`Done (v2.83.0)`) but wrong when handed a title/slug
(`review_prep...` -> `Review`). Audit **every** `canonical_status` caller for the
same trap - it must only ever receive a value extracted from the Status field/
column, never a title, slug, or free-prose cell. Candidates to check: reconcile
(index rows), status, review_prep, audit, integrity, resume. Consider tightening
the boundary rule or adding a guarded `status_from_row(row, col)` helper so the
column is positional, not inferred.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-06-20 | Autosprint (determinism-sprint) | Filed - surfaced by US0014's title during the sprint closing reconcile |
| 2026-06-20 | Autosprint (determinism-sprint retro) | Recurred live on CR0023's title ("Complete the conformance gate" -> status Complete) - confirms the class; raises severity for a positional-read fix |
