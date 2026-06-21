# CR-0041: progressive-disclosure indexes with release archival (RFC0012)

> **Status:** Complete
> **Priority:** High
> **Type:** Feature
> **Requester:** Darren Benson
> **RFC:** RFC-0012
> **Date:** 2026-06-20
> **Affects:** scripts/archive.py (new), scripts/reconcile.py (parse_index union), reference-outputs.md, reference-scripts.md, SKILL.md
> **Depends on:** CR0026 (reconcile apply / count recompute)
> **GitHub Issue:** --

## Summary

Delivers RFC0012 (full: WS1-WS4; explicit command, rows-only). A flat `_index.md` grows
O(n) and is loaded whole - mostly terminal rows (consuming repo B: 196 KB stories, 376 KB
CRs). Bound the live index by archiving terminal rows by release: the live index keeps
active rows + a bullet pointer; the terminal rows move to `<type>/archive/{release}/{type}.md`
(rows move, files stay). `reconcile`/`status` union the archive sub-indexes so the
census stays correct - the HIGH risk, contained.

## Proposed Changes

- **WS2** `reconcile.parse_index`: union `<type>/archive/**/*.md` rows with the live
  rows (refactored into `_index_rows_and_summary`), so archived artifacts are never
  `missing-row` and counts stay correct.
- **WS3** `scripts/archive.py archive --type <t> --release <r>`: move the master
  table's terminal rows into the archive sub-index, leave a bullet pointer, recompute
  counts (via the union-aware `apply`). Master table selected by its ID column; explicit;
  idempotent per release.
- **WS1** `reference-outputs.md`: the active/archive convention + summary-row/bullet schema.
- **WS4** `reference-outputs.md`: slice-read guidance for large indexes.

## Acceptance Criteria

- [x] `archive` moves a type's terminal master-table rows to `<type>/archive/{release}/{type}.md`, leaves a bullet pointer, and keeps non-terminal rows active; rows-only (files unchanged).
- [x] After archiving, `reconcile detect` shows **0 drift** (no missing-row for archived files, counts = active+archived) across one release, a second release, and a new active artifact added afterwards.
- [x] The archive pointer bullets are not ingested as rows; `apply` is idempotent on an archived board; the master table (not a secondary status view) is selected.
- [x] Unit-tested (census-correctness, master-table selection, idempotence); conventions documented; independent critic APPROVE (id-column hardening applied).

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-06-20 | Autosprint (RFC0012) | Complete - archive.py + parse_index union + conventions; critic APPROVE after hardening master-table selection to the ID column |
