# CR-0144: one shared structural table iterator in sdlc_md - retire the per-parser boundary bugs as a class

> **Status:** Approved
> **Priority:** High
> **Type:** Improvement
> **Date:** 2026-07-04
> **Created-by:** sdlc-studio file

## Summary

The same defect class surfaced three times in one day: BG0046 (duplicate-id scan tallying the Dependencies table into the previous scope), the sibling parsers _index_rows_and_summary/_index_row_ids caught by the independent critic (a closed bug's field failure still reproducible), and BG0049 (ts-check's matrix parser reading Revision History rows as ACs). CR0141 suggests product_reconcile.parse_feature_map is the next family member. Every parser hand-rolls its own table-boundary detection - vocabulary matches, stateful column pins - and each new parser re-imports the disease. Lesson L-0001 ('a parser-boundary fix must sweep every sibling parser sharing the assumption') implies the real fix: one shared iterator.

## Design (settled at the sprint design rung)

- **API:** `sdlc_md.iter_tables(text)` yields one record per table:
  `{header: [cells], rows: [[cells], ...], start_line}`. Boundaries are structural -
  a header row is a `|`-row immediately followed by its separator (any dash count,
  `_SEP_ROW_RE` semantics); a markdown heading ends the current table; a vocabulary
  header without a separator still opens a table (legacy tolerance, matching the
  parsers being ported).
- **Column pinning stays in the callers:** the iterator owns boundaries only; each
  parser keeps its own semantics (duplicates-kept for the id scan, header-pinned
  status/id columns, two-view union) so the ports change WHERE rows come from,
  never what is done with them.
- **Port order (one at a time, suite green between each):** `_index_row_ids` ->
  `_within_table_dup_counts` -> `_index_rows_and_summary` -> `verify_ac.ts_check`.
  Each port lands with its existing tests unmodified and passing - pinned
  behaviour is the regression harness.
- **Sweep last:** grep for residual hand-rolled boundary logic; the AC's sweep is
  a checklist item, not a code change.

## Acceptance Criteria

- [ ] sdlc_md gains a structural table iterator (yields per-table header cells + data rows, boundaries = header-plus-separator, any dash count, headings end scope) with its own unit tests
- [ ] the known table parsers (reconcile duplicate scan, _index_rows_and_summary, _index_row_ids, verify_ac.ts_check) are ported onto it with behaviour pinned by their existing tests (product_reconcile was retired by CR-0142 before this CR could port it)
- [ ] a repo sweep confirms no remaining hand-rolled table-boundary logic outside the shared helper; CHANGELOG [Unreleased]

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-04 | audit | Raised |
| 2026-07-04 | claude | Design settled: iterator API, caller-owned pinning, port order (one at a time, tests unmodified) |
