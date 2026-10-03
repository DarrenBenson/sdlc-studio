# BG0889: A padded index table holding a wide character still fails MD060 after a row in it is rewritten

> **Status:** In Progress
> **Severity:** Low
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/lib/sdlc_md.py, .claude/skills/sdlc-studio/scripts/tests/test_lean_index_wide_alignment.py, .claude/skills/sdlc-studio/scripts/tests/test_lean_index_row_style.py, changelog.d/BG0889.md
> **Evidence:** BG0867 QA review round 2 (RUN-01M3VF2J)
> **Created:** 2026-10-01
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-10-01T19:08:32Z

## Summary

BG0867 re-aligns only the table a write touched and leaves any table holding a wide, combining or format character alone, because Python len() is not markdownlint's display width. A padded table holding such a character, with a row rewritten by reconcile, therefore still fails MD060, as before BG0867.

## Steps to Reproduce

1. A padded test-spec index table holding a CJK cell. 2. transition.py set one of its rows -> markdownlint MD060 on that row.

## Proposed Fix

Measure display width as markdownlint's string-width does (east-asian W/F as 2, combining and format as 0) and align those tables too.

## Acceptance Criteria

- [ ] **AC1** Given a lint-clean test-spec index whose padded table holds a CJK title cell (`第二の仕様`, padded by display width), when `transition.py set --id TS0001 --status Complete --root <fixture>` rewrites another row of that table, then markdownlint with this repository's config reports no MD060 on the index.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_index_wide_alignment.py::IndexWideAlignmentTests::test_a_cjk_table_is_realigned_after_a_rewrite
  - **Verified:** yes (2026-10-03)
  - **Fails-on:** HEAD leaves the table alone (BG0867's wide-character skip), so the rewritten row stays compact and MD060 fails on it
- [ ] **AC2** Given a padded table holding a cell with a combining mark (`e` followed by U+0301) and one row written compact, when `sdlc_md.align_padded_tables(text, original)` runs, then markdownlint reports no MD060 on the result, and a table no row of which changed is still returned byte for byte.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_index_wide_alignment.py::IndexWideAlignmentTests::test_a_combining_mark_is_measured_as_zero_width
  - **Verified:** yes (2026-10-03)
  - **Fails-on:** HEAD returns the table unchanged, and a width measured with `len()` puts the mark's row one column out

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-01 | sdlc-studio | Filed |
| 2026-10-01 | engineering seat (groomer) | Groomed: premise executed at 7fa77f8e: a lint-clean padded test-spec index holding `第二の仕様`, `transition.py set --id TS0001 --status Complete` -> the rewritten row stays compact and markdownlint reports MD060 at line 7 (three pipes); criteria authored, Affects set (the BG0867 test pinning the skip changes with it), Points kept at 2 |
