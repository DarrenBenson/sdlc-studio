# CR-0153: reconcile diagnoses a mis-named/absent Status column once, not N per-row false mismatches

> **Status:** Proposed
> **Created:** 2026-07-04
> **Created-by:** sdlc-studio new
> **Priority:** High
> **Type:** Improvement
> **Affects:** scripts/reconcile.py (`parse_index` status-column detection + a new pre-check finding)
> **Found by:** a second consuming project adopting the skill - not skill self-dogfooding

## Summary

A real consuming project named its CR index status column **`Effective Status`**
(a deliberate richer rollup - cells carry qualifiers like `Complete (docs)`, `Built (v2.315.0)`).
`reconcile.py:110` locates the column by an **exact** match, `"status" in lowered`, chosen to
avoid scavenging the `Dependency Status` cell of the cr.md dependencies table. So `Effective
Status` is not recognised, `status_col` stays `None`, and **every one of ~302 rows reads
`Unknown`** - producing 302 `status-mismatch` findings plus a `count-mismatch`, all false. The
statuses were in fact fine (`_canonical_status` parses the qualified cells correctly once the
column is found); only the header name defeated detection.

The failure is not the strictness - it is that the tool **buries the structural cause in
per-row noise**. 302 mismatches read as catastrophic drift; the operator has no signal that the
real issue is one mis-named column. `project_upgrade.py` does not help: it explicitly refuses to
rewrite per-type index headers ("guessing per-type index headers would over-reach") and only
re-surfaces the same drift as a generic "review with reconcile" note. A human had to eyeball the
header to find it.

This is the **same class as CR0141** (product_reconcile: "PF rows present but none parsed - make
it one blocking, *named* finding, not a silent/confusing pass"). Twice now the table parsers fail
by drowning the structural cause instead of naming it once. It is worth a general guard.

## Proposed change

Add a **pre-check** in `reconcile.py` that runs before per-row comparison, per index:

1. **Detect the degenerate parse.** If an `_index.md` has >=1 data row but **every** row's
   `index_status` is `Unknown` (or the primary table declares no `Status` column while carrying
   status-like data), do **not** emit per-row `status-mismatch` findings for that index.
2. **Emit one diagnostic instead**, naming the cause and the fix, e.g.:
   `change-requests/_index.md: no 'Status' column found (header has 'Effective Status'); all 302
   rows read Unknown. Rename the column to 'Status', or run project upgrade.` Include the offending
   header cell so the operator sees exactly what to change.
3. **Keep the Dependency-Status guard.** The fix is detection + a clear message, not loosening the
   column match - so the deliberate exact-match (avoiding `Dependency Status`) stays; the new
   signal only fires when the *whole index* fails to parse, which the nested-table false-positive
   never triggers.
4. Optionally, `project_upgrade.py` promotes this from needs-judgment to an offered safe correction
   (rename the header) once reconcile has named it - but the reconcile diagnostic is the load-bearing
   half and stands alone.

## Acceptance Criteria

- [ ] An index with data rows whose status column is named other than `Status` (e.g. `Effective
      Status`) yields **one** diagnostic naming the header + the rename/upgrade remedy - not one
      `status-mismatch` per row.
- [ ] The diagnostic fires only on whole-index parse failure (all rows `Unknown`); a healthy index
      with one genuinely-drifted row still reports that single `status-mismatch` as today.
- [ ] The `Dependency Status` nested-table false-positive stays suppressed (the exact-match guard
      is unchanged); a regression test pins both the new diagnostic and the unchanged guard.
- [ ] A regression test seen to fail before the fix (mutation-checked): a fixture index with an
      `Effective Status` header asserts one diagnostic, zero per-row mismatches.

## Notes / provenance

Found while planning a sprint in a second consuming project with the new skill: the very
first `reconcile detect` reported 303 drift items, all false, and the cause (`Effective Status`
header) took manual eyeballing to find. Resolved in that project by renaming the column to `Status`
(values already parsed, so zero rows were rewritten). The skill-side gap is that neither reconcile
nor project upgrade diagnosed it. Sibling: CR0141 (same rows-present-but-none-parsed pattern in
product_reconcile, now retired by CR0142 - but the lesson is the parsers should name the structural
cause once).

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-04 | Claude (cross-project dogfooding) | Created via `new` (deterministic) |
| 2026-07-04 | Claude (cross-project dogfooding) | Filled in from the consuming-project adoption: `Effective Status` header defeats reconcile's exact `status` match, yielding 302 false mismatches; propose a whole-index degenerate-parse pre-check that names the cause once. Same class as CR0141. |
