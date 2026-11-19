# BG1621: The TRD's table of committed records does not list the author mutant lists that critic.py self-check record now keeps under sdlc-studio/reviews/author-mutants/

> **Status:** Open
> **Severity:** Low
> **Points:** 1
> **Affects:** sdlc-studio/trd.md, tools/tests/test_lean_trd_refresh.py, changelog.d/BG1621.md
> **Evidence:** run eighteen, 2026-11-19: lane L6 builder's hand-back; the file is outside both units' Affects
> **Created:** 2026-11-19
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-19T15:10:57Z

## Summary

Run eighteen's self-check work (`critic.py self-check record --mutants-from`) keeps each unit's full mutant list as a committed file, `sdlc-studio/reviews/author-mutants/<id>.json`, so the QA brief can replay it. trd.md section 6's table of committed records (around line 552, beside `author-self-checks.md`) names every other record the scripts commit but not this one, so the TRD no longer says where the tool writes.

## Steps to Reproduce

Record a self-check with `--mutants-from <runner report>`, then read trd.md section 6: the new file under sdlc-studio/reviews/author-mutants/ has no row.

## Proposed Fix

Add a row for the author mutant lists to the committed-records table, naming the writer and the reader (the QA brief's replay).

## Acceptance Criteria

- [ ] **AC1** Given trd.md section 6's table of committed records, when it is read, then it has a row for `sdlc-studio/reviews/author-mutants/<id>.json` that names `critic.py self-check record --mutants-from` as its writer and the QA brief's replay of the author's mutants as its reader
  - **Verify:** pytest tools/tests/test_lean_trd_refresh.py::TrdStorageTests::test_the_committed_records_table_lists_the_author_mutant_lists

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-19 | sdlc-studio | Filed |
