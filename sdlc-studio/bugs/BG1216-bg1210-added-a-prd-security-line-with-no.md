# BG1216: BG1210 added a PRD Security line with no TSD row, so the TSD refresh test fails on main

> **Status:** Fixed
> **Severity:** Medium
> **Points:** 1
> **Affects:** sdlc-studio/prd.md, sdlc-studio/tsd.md, changelog.d/BG1216.md
> **Evidence:** BG1183 builder report, round 3, 2026-11-04.
> **Created:** 2026-11-04
> **Created-by:** sdlc-studio file
> **Raised-by:** claude; human; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-04T18:04:00Z

## Summary

2026-11-04, found by BG1183's round-3 commit hook (run five). BG1210 added the Cursor usage call to the PRD's Security NFR. tools/tests/`test_lean_tsd_refresh.py`::TsdRefreshTests::`test_every_prd_nfr_has_a_tsd_row` requires every PRD NFR clause to map to a TSD row, and failed with no row for the new clause; the bullet's internal semicolon also split it into two clauses. BG1210's review ran only the PRD test it named, and the hook selection for BG1210's commit did not reach this one.

## Steps to Reproduce

1. `python3 -m pytest -q tools/tests/test_lean_tsd_refresh.py::TsdRefreshTests::test_every_prd_nfr_has_a_tsd_row` at 457ac6c7.

## Proposed Fix

Make the PRD bullet one clause and add a TSD Security row naming the test that pins the Cursor call.

## Acceptance Criteria

- [ ] **AC1** Every PRD NFR clause, the Cursor usage call among them, maps to a TSD row, and the PRD refresh test still passes.
  - **Verify:** pytest tools/tests/test_lean_tsd_refresh.py tools/tests/test_lean_prd_refresh.py
  - **Verified:** yes (2026-11-04)

## Impact

Main's suite is red, and every commit whose selection reaches the TSD test is refused.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-04 | claude | Filed |
