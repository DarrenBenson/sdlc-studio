# BG0043: reconcile apply drops bold-markup CR-index row statuses and skips the CR-summary recompute

> **Status:** Closed
> **Created:** 2026-06-25
> **Created-by:** sdlc-studio new
> **Severity:** medium

## Summary

`reconcile apply` **reports edits it did not make** - the sharpest defect a field upgrade surfaced.
On a CR index it printed `set cr CR-0265: Proposed -> Complete` and "recomputed story summary", but
`git status` showed the CR index unmodified. Two distinct failures, both silent:

- It does not persist a row whose Status cell is bold-wrapped (`| **Complete** |`). The reader pins
  the status column by header and canonicalises the token, but the writer's match/replace misses the
  bold-wrapped cell, so the row is left untouched while the run claims it changed.
- It will not recompute the CR **summary** block at all, because the CR index carries two different
  table formats (a dual-layout index); the summary recompute path does not handle the second layout.

The fatal part is the reporting: it announced the status flip and a summary recompute, then wrote
nothing, presenting a no-op as a clean apply. A tool that claims an edit it didn't make is worse than
one that errors - the operator had to hand-verify every count against the file census and hand-edit
the CR rows and summary. Stale summaries then sit under confident dated "recount from file census"
annotations, so a wrong number wears a provenance note (the downstream of this same write gap).

## Steps to Reproduce

1. A CR `_index.md` with bold-wrapped status cells (`| CR-0265 | ... | **Proposed** |`) and a
   dual-format layout (row table + a differently-shaped summary block).
2. Flip CR-0265 to Complete in its file; run `reconcile apply` (or the equivalent set/apply path).
3. It prints `set cr CR-0265: Proposed -> Complete` and a summary recompute, exits as if clean.
4. `git status` / `git diff` shows the index unchanged. The reported edit never landed.

## Proposed Fix

Two fixes plus a reporting guard: (a) the writer must match a status cell regardless of inline
emphasis - strip `**`/`*`/backticks before matching and re-wrap on write, mirroring the reader's
tolerant canonicalisation; (b) the summary recompute must handle the dual table format (or detect and
report "summary not in a recomputable layout" rather than silently skipping); (c) **never report a
change that was not persisted** - verify the write (diff the buffer) and, if a targeted edit matched
nothing, surface it as a warning/error, not as "changed 0 rows / clean". Unit tests: a bold-wrapped
status row is persisted; a dual-format summary recomputes or is reported unrecomputable; a claimed
edit that doesn't apply raises rather than reports success. Sibling of [[BG0044]] (the per-epic
count-block defect); both are reconcile-writer correctness. CHANGELOG.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-06-25 | field | Created via `new` (deterministic) |
