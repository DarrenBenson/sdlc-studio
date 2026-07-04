# BG0044: reconcile flattens per-epic Done count blocks corrupting per-section sub-tables

> **Status:** Closed
> **Created:** 2026-06-25
> **Created-by:** sdlc-studio new
> **Severity:** high

## Summary

`reconcile` stamps the global status total into every per-section count sub-table, flattening
per-epic `Done | N` blocks. An index that carries small per-epic count tables (one per epic section)
has each of those overwritten with the project-wide totals, corrupting the per-section breakdown. This
was first hit in the field on a consuming project and has sat as a known-but-unfiled defect; a second upgrade
run re-confirmed it as a standing hazard - the operator kept `--with-reconcile` OFF and diffed every
index by hand precisely because of this, even though that particular index turned out to have no
per-epic blocks (so the bug could not fire there). The fear was justified but unquantifiable up front,
which taxed every reconcile decision in the run.

## Steps to Reproduce

1. An `_index.md` with a canonical summary table AND one or more per-epic count sub-tables of the form
   `| Status | N |` scoped to a single epic section.
2. Run `reconcile` (the count recompute path).
3. The per-epic sub-tables are overwritten with the global totals instead of their per-section counts.

## Proposed Fix

Scope the count recompute to the **canonical** summary block only - identify the project-level summary
(by position/header) and recompute that one, leaving per-section `| Status | N |` sub-tables untouched
(or recompute each against its own section's census). The recompute must not treat every two-column
status/int table as the global summary. Unit test: an index with a global summary plus two per-epic
count blocks recomputes only the global summary; the per-epic blocks keep their section-scoped counts.
Sibling of [[BG0043]] (reconcile-writer correctness). Once fixed, the standing "keep reconcile off and
diff by hand" caution can be retired. CHANGELOG.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-06-25 | field | Created via `new` (deterministic) |
