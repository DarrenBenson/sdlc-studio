# BG0066: append_index_row scans unbounded and disagrees with reconcile on the master data table

> **Status:** Closed
> **Created:** 2026-07-06
> **Created-by:** sdlc-studio new
> **Severity:** Medium
> **Raised-by:** Sam Eriksson (QA amigo), repository review RV0006
> **Effort:** M

## Summary

The create path and the reconcile path use two different rules for "which table is the master
data table". `file_finding.append_index_row` inserts after the last `| [`-prefixed line
anywhere in the file, while `reconcile._master_data_header` census-ranks candidate tables
precisely to stop a trailing view table capturing an appended row. In a layout where the
master table is not last, `artifact new`/`file_finding` appends into the wrong table.

## Evidence

- Create path: `.claude/skills/sdlc-studio/scripts/lib/sdlc_md.py:160-169`
  (`find_data_header` returns the last header with an ID column);
  `file_finding.py:135-137` (`append_index_row` inserts after the last `"| ["`-prefixed line
  anywhere in the file).
- Reconcile path: `reconcile.py:788-825` (`_master_data_header` census-ranks tables "A
  trailing view or breakdown table must never capture an appended row").
- `artifact.py:241-247` (`meta_new`) already re-fixed the unbounded scan for meta indexes
  ("stop at the first non-table line"), but `append_index_row` - used by every pipeline `new`
  - still scans unbounded.

## Impact

The shipped templates put the master table last, so the bug is latent; but house layouts are
explicitly supported via `conventions:`, and a misfiled row produces the "row lands in the
wrong table" drift class the lib docstrings say was already retired.

## Steps to Reproduce

1. Use an index layout where a linked-row or breakdown table follows the master data table.
2. `artifact.py new` (or `file_finding`) to append a row.
3. The row lands in the trailing table; `reconcile detect` then reports the drift under its
   different pinning rule.

## Proposed Fix

Bound `append_index_row`'s insertion to the contiguous rows of the pinned table (as
`meta_new` does), and converge both paths on a single `_master_data_header` moved into
`lib/sdlc_md.py`. (Broader create-path/reconcile-path convergence relates to CR0181.)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-06 | Sam Eriksson (QA amigo) | Created via `new` (deterministic) |
| 2026-07-06 | Sam Eriksson (QA amigo) | Evidence verified; filed from RV0006 architecture leg |
| 2026-07-06 | Dani Okafor (Engineering amigo) | Fixed with a failing-first regression test on branch sprint/rv0006-bugfixes; transitioned to Closed |
