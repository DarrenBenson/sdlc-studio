# BG1221: BG1187's side-by-side test hand-lists three .py names, so the push gate's hand-copied-list census fails

> **Status:** Open
> **Severity:** Medium
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/scripts/tests/test_verify_ac.py, changelog.d/BG1221.md
> **Evidence:** Push gate at 778187c1 on devserver1, scratchpad run5/push2.log.
> **Created:** 2026-11-04
> **Created-by:** sdlc-studio file
> **Raised-by:** claude; human; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-04T20:40:50Z

## Summary

2026-11-04, the push gate at 778187c1 after run five's close. tools/tests/`test_test_census.py`::HandCopiedMirrorTests::`test_no_new_hand_copied_script_list` matches three consecutive quoted `.py` names in a test file and named `test_verify_ac.py`, whose StampsCollectSideBySideTests (BG1187, 457ac6c7) passes the fixture list a.py, b.py, cached.py at line 3535. They are fixture names, not shipped scripts, but the census reads the content. No commit hook selected the census module.

## Steps to Reproduce

1. `python3 -m pytest -q tools/tests/test_test_census.py::HandCopiedMirrorTests::test_no_new_hand_copied_script_list`.

## Proposed Fix

Build the fixture list from its stems so the test names no three script literals.

## Acceptance Criteria

- [ ] **AC1** The hand-copied-list census passes, and StampsCollectSideBySideTests still passes.
  - **Verify:** pytest tools/tests/test_test_census.py::HandCopiedMirrorTests .claude/skills/sdlc-studio/scripts/tests/test_verify_ac.py::StampsCollectSideBySideTests

## Impact

The push gate is red, so main cannot be pushed.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-04 | claude | Filed |
