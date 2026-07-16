# CR-0182: Consolidate the two archive implementations on sdlc_md.iter_tables

> **Status:** Complete
> **Size:** M
> **Created:** 2026-07-06
> **Created-by:** sdlc-studio new
> **Epic (v4 breakdown):** [EP0018](../epics/EP0018-tooling-hardening-and-review-debt.md)
> **Priority:** Medium
> **Type:** Improvement
> **Raised-by:** Sam Eriksson (QA amigo), repository review RV0006
> **Effort:** M

## Summary

Two parallel archive implementations exist - `archive.py` (release-based, own table walkers)
and `reconcile.py` (`archive_plan`/`archive_type`, its own hand-rolled line walker). They have
different destinations, different terminal sets (BG0061), and duplicated table-parsing that
both bypass `sdlc_md.iter_tables`, the declared single structural boundary rule.

## Motivation

The duplicated walkers re-import the defect class `iter_tables` was built to retire.
`reconcile.archive_plan` reassigns `header` per table (reconcile.py:1151) yet moves rows from
every status+id table under the single last-seen header (reconcile.py:1178), so a multi-view
index - the shipped story layout - can archive one story twice and misalign columns. Two
shipped commands doing overlapping "relocate terminal index rows to an archive sub-index" work
with divergent rules is a standing correctness and maintenance risk.

## Scope

**In scope**

- Consolidate on one archiver, or make one delegate to the other; single destination
  convention.
- Rebuild both row-selection passes on `sdlc_md.iter_tables` with per-table headers so a
  multi-view index cannot double-archive or misalign.
- Adopt `sdlc_md.terminal_statuses(type_)` as the single terminal-set source (subsumes BG0061).

**Out of scope**

- Changing the archive-on-release policy or archival thresholds (CR0160 already tunes those).
- The index-bloat advisory (exists).

## Acceptance Criteria

- [ ] One archiver, or a documented delegation; the other is a thin wrapper or removed.
- [ ] A multi-view story index fixture archives each terminal row exactly once with aligned
      columns (regression test proving the current double-archive path is closed).
- [ ] Both archive paths use `sdlc_md.terminal_statuses`; BG0061's Deferred mis-classification
      cannot recur.
- [ ] No hand-rolled table walkers remain in `archive.py`/`reconcile.py` archive paths.

## Dependencies

| Artefact | Relationship |
| --- | --- |
| BG0061 | Subsumed: the terminal-set fix lands here (or BG0061 first, this consolidates) |
| CR0187 | Themed code-quality debt; this duplication is significant enough to pull out separately |

## Risk

Archival edits live indexes; a consolidation bug could relocate a live row or lose one.
Mitigate with the multi-view fixture test and a dry-run diff before apply.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-06 | Sam Eriksson (QA amigo) | Created via `new` (deterministic) |
| 2026-07-06 | Sam Eriksson (QA amigo) | Full scope drafted from RV0006 code-level leg |
