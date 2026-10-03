# BG0920: The close checklist's cost row reads the moved meter on a re-close while the re-filed page reads the first close's

> **Status:** In Progress
> **Severity:** Low
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/sprint_report.py, .claude/skills/sdlc-studio/scripts/tests/test_lean_reclose_checklist_cost.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py
> **Created:** 2026-10-03
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-10-03T00:47:20Z

## Summary

After BG0913 and BG0916, a re-close re-files a page whose main-thread tokens keep the first close's reading (4,000), but the close checklist's cost row (`_ck_cost)` still reads the live meter (13,000), so the operator sees two token figures for one run.

## Steps to Reproduce

1. Close a run, filing a page. 2. Take a later meter stamp. 3. Re-close: the page reads 4,000, the checklist's cost row 13,000.

## Proposed Fix

Read the checklist cost row from the same window the re-filed page uses. No new refusal.

## Acceptance Criteria

- [ ] **AC1** Given a re-close whose re-filed page reads 4,000 main-thread tokens after a later meter stamp, when the close checklist is printed, then its cost row reads 4,000 too. Fails on: the current checklist, which reads 13,000
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_reclose_checklist_cost.py::RecloseChecklistCostTests::test_the_checklist_cost_row_matches_the_page

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-03 | sdlc-studio | Filed |
