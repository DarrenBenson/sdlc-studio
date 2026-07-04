# CR-0144: one shared structural table iterator in sdlc_md - retire the per-parser boundary bugs as a class

> **Status:** Proposed
> **Priority:** High
> **Type:** Improvement
> **Date:** 2026-07-04
> **Created-by:** sdlc-studio file

## Summary

The same defect class surfaced three times in one day: BG0046 (duplicate-id scan tallying the Dependencies table into the previous scope), the sibling parsers _index_rows_and_summary/_index_row_ids caught by the independent critic (a closed bug's field failure still reproducible), and BG0049 (ts-check's matrix parser reading Revision History rows as ACs). CR0141 suggests product_reconcile.parse_feature_map is the next family member. Every parser hand-rolls its own table-boundary detection - vocabulary matches, stateful column pins - and each new parser re-imports the disease. Lesson L-0001 ('a parser-boundary fix must sweep every sibling parser sharing the assumption') implies the real fix: one shared iterator.

## Acceptance Criteria

- [ ] sdlc_md gains a structural table iterator (yields per-table header cells + data rows, boundaries = header-plus-separator, any dash count, headings end scope) with its own unit tests
- [ ] the known table parsers (reconcile duplicate scan, _index_rows_and_summary, _index_row_ids, verify_ac.ts_check) are ported onto it with behaviour pinned by their existing tests (product_reconcile was retired by CR-0142 before this CR could port it)
- [ ] a repo sweep confirms no remaining hand-rolled table-boundary logic outside the shared helper; CHANGELOG [Unreleased]

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-04 | audit | Raised |
