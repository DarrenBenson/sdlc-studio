# BG0026: reconcile count-block rewrite stamps global total into per-epic count sub-tables

> **Status:** Fixed
> **Created:** 2026-06-22
> **Created-by:** sdlc-studio new
> **Severity:** High

## Summary

`reconcile --apply` (called by gate/autosprint/project upgrade) recomputes index summary counts. An index can carry many `| Status | Count |` tables (per-epic roll-ups) plus one global summary; the old code stamped the GLOBAL total into EVERY one. On a consuming project it overwrote each per-epic `| Done | 6 |` with the fleet total (590) - silent index corruption, caught only by diffing before commit.

## Steps to Reproduce

Run `reconcile --apply` (or `project upgrade --apply`) on a project whose stories/_index.md has per-epic `| Status | Count |` sub-tables -> every per-epic count becomes the global total.

## Proposed Fix

`_rewrite_index_lines` now recomputes only a CANONICAL summary: a `Status|Count` block carrying a `**Total**` row (template signature), or the sole summary in the file. Per-epic tables (no Total, file has >1 summary) are left to the author. Verified on a real consuming-project index (read-only): now plans 0 count changes. Doc note in reference-reconcile.md.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-06-22 | sdlc | Created via `new` (deterministic) |
