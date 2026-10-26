# BG1131: The close checklist's cost row never reads a run holding only its legacy baseline, and its main-thread-only re-derivation note has no test

> **Status:** Open
> **Severity:** Low
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint_report.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py, .claude/skills/sdlc-studio/scripts/tests/test_close_checklist_cost_paths.py, changelog.d/BG1131.md
> **Evidence:** US1097 QA review round 2, qa-seat-US1097-r1, 2026-10-26, at 979c2d83: one new low and one pre-existing finding.
> **Created:** 2026-10-26
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-10-26T13:35:28Z

## Summary

US1097's round-2 QA review (APPROVE, 2026-10-26). (1) `_ck_cost` passes no closing reading (`sprint_report.py`:1911, the same at e877a6b9), so on a run holding only its legacy baseline the checklist says 'unattributed' while the page reads 2,975; only a preview shows it, since the close stamps first. (2) The re-derivation note on the checklist's main-thread-only branch (`sprint_report.py`:1934) can be removed with 1,103 tests across seven modules green; a scratch test with no subagents directory kills it.

## Steps to Reproduce

Build the checklist for a run with its stamps emptied: unattributed. Remove the note at `sprint_report.py`:1934 and run the meter modules: green.

## Proposed Fix

Pass the closing reading to `_ck_cost` as `build_report` now does; add a no-subagents subtest asserting the main-thread branch names the re-derivation.

## Acceptance Criteria

- [ ] **AC1** Given a run holding only its legacy baseline, then the close checklist's cost row reads the same figure as the page
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_close_checklist_cost_paths.py::CloseChecklistCostPathsTests::test_a_legacy_baseline_only_run_reads_as_the_page_does
- [ ] **AC2** Given a main-thread-only run with a re-derived reading, then the checklist's cost detail names the re-derivation
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_close_checklist_cost_paths.py::CloseChecklistCostPathsTests::test_the_main_thread_branch_names_the_re_derivation

## Impact

A preview of the close checklist disagrees with the page on a legacy-baseline run, and one stated behaviour is unpinned.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-26 | Claude Opus 5.5 | Filed |
