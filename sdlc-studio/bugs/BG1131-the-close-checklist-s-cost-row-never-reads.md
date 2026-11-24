# BG1131: The close checklist's cost row never reads a run holding only its legacy baseline, and its main-thread-only re-derivation note has no test

> **Status:** Fixed
> **Severity:** Low
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint_report.py, .claude/skills/sdlc-studio/scripts/tests/test_close_checklist_cost_paths.py, changelog.d/BG1131.md
> **Evidence:** US1097 QA review round 2, qa-seat-US1097-r1, 2026-10-26, at 979c2d83: one new low and one pre-existing finding.
> **Created:** 2026-10-26
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-10-26T13:35:28Z

## Summary

(1) `_ck_cost` passes no closing reading (`sprint_report.py` `_ck_cost`; `build_report` passes `current, current_path` for a run with a legacy baseline and no stamps), so on a run holding only its legacy baseline the checklist says 'unattributed' while the page reads a figure. Reproduced at HEAD cecc9dfe7: `_ck_cost` over a baseline-only run returns `unattributed`. (2) The `rebased` clause in `_ck_cost`'s detail is not pinned by any checklist test; `test_meter_reads_true.py` pins `rebased_note` itself, not the row.

## Steps to Reproduce

Build the checklist for a run with its stamps emptied: unattributed. Remove the note at `sprint_report.py`:1934 and run the meter modules: green.

## Proposed Fix

Pass the closing reading to `_ck_cost` as `build_report` now does; add a no-subagents subtest asserting the main-thread branch names the re-derivation.

## Acceptance Criteria

- [ ] **AC1** Given a run holding only its legacy session_token_baseline and a readable closing session, when the close checklist is built, then its cost row reads the same measured figure as the report page. Fails on: `_ck_cost` calls `run_token_total(metered)` with no closing reading (`_ck_cost` in sprint_report.py), so the row reads 'unattributed' while the page reads a figure.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_close_checklist_cost_paths.py::CloseChecklistCostPathsTests::test_a_legacy_baseline_only_run_reads_as_the_page_does
  - **Verified:** yes (2026-11-24)

- [ ] **AC2** Given a measured run whose total re-derived one reading on an earlier counting basis, when the checklist's cost row is built, then its detail carries `run_state.rebased_note` for that total. Fails on: no test pins the note, so removing `rebased` from the `_ck_cost` detail leaves every module green.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_close_checklist_cost_paths.py::CloseChecklistCostPathsTests::test_the_cost_detail_names_the_re_derivation
  - **Verified:** yes (2026-11-24)

## Impact

A preview of the close checklist disagrees with the page on a legacy-baseline run, and one stated behaviour is unpinned.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-26 | Claude Opus 5.5 | Filed |
| 2026-11-24 | Sam Eriksson (qa) | Groomed for run twenty-five: ACs made executable with Fails-on and the true test class; summary updated to HEAD |
