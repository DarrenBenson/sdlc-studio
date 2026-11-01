# BG1163: The TRD's lifecycle table states a tracked record is filed on every close, which --file-and-close does not do, and the .local writer pin accepts an orphaned writer

> **Status:** Open
> **Severity:** Medium
> **Points:** 3
> **Affects:** sdlc-studio/trd.md, tools/tests/test_lean_trd_refresh.py, .claude/skills/sdlc-studio/scripts/tests/test_lean_v61_review_residue.py, changelog.d/US1100.md
> **Evidence:** sdlc-studio/reviews/critic-verdicts.md, US1100 APPROVE by qa-seat-US1100-r1 (brief dddd8305722e): mutants D, E, F and M6 survive.
> **Created:** 2026-11-01
> **Created-by:** sdlc-studio file
> **Raised-by:** claude; human; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-01T07:26:40Z

## Summary

qa-seat-US1100-r1's APPROVE of US1100 (2026-11-01) found: (1) trd.md:540-541 shows only the route that ends in a signature, and its close row says the close files the run report and the tracked record. `sprint.py close --file-and-close` returns at sprint.py:9479, before `_file_awaiting_record` (:9629), so on that route no tracked record is filed; `stop` and `close --apply-signoff` also close the live record through `run_state.close_run` without reaching `run_state.file_tracked`, and the TRD names none of them. (2) The pin in `test_lean_v61_review_residue.py` counts any def that writes the file as a writer, whether or not anything calls it: removing both `note_brief(...)` call sites in critic.py left the pin green. changelog.d/US1100.md:20-21 over-claims. (3) The pin identifies the file by its last segment only (:178), so moving `GOAL_REVIEW_REL` out of .local passes. (4) The page check ignores negation (:84, :332). (5) AC2's test keys the run-state rows by path and never reads the label column, so swapping Live and Tracked labels passes. (6) The claim-drift row's writer cell (trd.md:513) names US0597, but both files were last changed in c906e153 (US0577).

## Steps to Reproduce

1. Read trd.md:540-541, then trace `sprint.py close --file-and-close`: it returns at :9479 before the tracked record is filed.
2. In a throwaway worktree replace critic.py's two `note_brief` calls with a no-op and run the pin: green.
3. Swap the Live and Tracked labels in the Run state table and run TrdStorageTests: green.

## Proposed Fix

Give the lifecycle table the stop and file-and-close routes, with what each files. Count a def-level writer only when shipped code calls it or a parser dispatches to it. Match the file by its full relative path. Refuse a negated write line on a page. Key the run-state rows by label as well as path. Correct the claim-drift writer cell from git.

## Acceptance Criteria

- [ ] **AC1** The TRD's lifecycle names stop and close --file-and-close and says what each files, and a test fails if a close route that reaches `run_state.close_run` is unnamed.
  - **Verify:** pytest tools/tests/test_lean_trd_refresh.py
- [ ] **AC2** The pin fails when a documented writer exists but nothing calls it, and when the file moves out of the documented directory.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_v61_review_residue.py
- [ ] **AC3** Swapping the Live and Tracked labels fails TrdStorageTests.
  - **Verify:** pytest tools/tests/test_lean_trd_refresh.py

## Impact

A TRD sentence is false for one close route, and the pin can pass with a documented file written by nothing.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-01 | claude | Filed |
