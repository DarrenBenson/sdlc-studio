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

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-06-20 | Autosprint (determinism-sprint) | Filed - surfaced by US0014's title during the sprint closing reconcile |
