# BG0046: duplicate-id gate trips on the CR index template's own Dependencies table (per-table reset misses headers without a bare "Status" cell)

> **Status:** Open
> **Created:** 2026-07-04
> **Created-by:** field report (a consuming project's sprint retro, 2026-07-04)
> **Severity:** medium

## Summary

`reconcile.detect_duplicate_rows` (surfaced as the gate's `duplicate-id` check) counts the rows of a
CR index's **Dependencies** table against the "All Change Requests" table, reporting one duplicate id
per CR that declares a dependency - on the exact table shape `templates/indexes/cr.md` ships
(`| CR | Depends On | Dependency Status |`). A fully-templated project fails its own gate.

Root cause: `_within_table_dup_counts` resets its per-table tally only on a header row satisfying
`len(cells) > 2 and "status" in lowered` - an **exact cell match**. The Dependencies header's cell is
`"dependency status"`, not `"status"`, so no reset fires; its rows are tallied inside the preceding
table's scope, and the fallback id extraction picks the bare `CR-xxxx` in column 1. Empirically (post
v3.3.0): a two-table snippet in the template's shape yields `{'CR0001': 2, 'CR0007': 2}`.

Field impact (a consuming project, 2026-07-04): `gate: FAIL` with `12 duplicate id(s) (0 file,
12 index-row)` - one per row of a healthy Dependencies table. The project had to convert the table to
prose to get the release gate green.

## Steps to Reproduce

1. Create a CR `_index.md` with the standard "All Change Requests" table plus the
   `templates/indexes/cr.md` Dependencies table (`| CR | Depends On | Dependency Status |`), each CR
   listed once per table.
2. Run `scripts/gate.py --only duplicate-id` (or `reconcile.detect_duplicate_rows`).
3. Every CR with a Dependencies row is reported as a within-table duplicate; the gate FAILs.

## Proposed Fix

Make the table-boundary detection structural rather than vocabulary-based: reset the tally on **every**
header row (a `|`-row immediately followed by a `| --- |` separator), not only headers containing a
bare `status` cell - a Dependencies row would then tally once within its own table and no duplicate is
reported. (A narrower patch - substring-match `any("status" in c for c in lowered)` - also clears this
shape but keeps the vocabulary coupling.) Add a regression test that renders `templates/indexes/cr.md`
with two CRs + dependency rows and asserts `detect_duplicate_rows` returns none - the gate validated
against its own shipped template (LL0010), same discipline as [[BG0045]]. Note the true-positive case
must stay caught: the same id twice within ONE table still flags. CHANGELOG.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-04 | field | Reported from a consuming project's sprint close (retro lesson / decisions ledger) |
