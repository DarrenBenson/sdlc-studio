# BG0766: The test census is red on main: a Sprint 4 test module holds a hand-copied script list and another has no census home

> **Status:** In Progress
> **Severity:** High
> **Points:** 1
> **Affects:** tools/tests/test_test_census.py, .claude/skills/sdlc-studio/scripts/tests/test_lean_lane_history.py
> **Created:** 2026-09-25
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-09-25T08:56:16Z

## Summary

tools/tests/`test_test_census.py` fails twice at main a71a9577: HandCopiedMirrorTests flags `test_lean_lane_history.py` (US0931) for a literal list of script names, and RealRepoTests counts 34 unattributed test files against a declared baseline of 33, so one module added this sprint has no census subject. The push's full suite refuses on both.

## Steps to Reproduce

python3 -m pytest tools/tests/`test_test_census.py` at main: 2 failed (`test_no_new_hand_copied_script_list` names `test_lean_lane_history.py`; `test_this_repos_test_files_are_mostly_attributed` reads 34 against 33).

## Proposed Fix

Derive `test_lean_lane_history.py`'s script names instead of listing them (or mark the list HAND-MAINTAINED ON PURPOSE with why), and give the newly unattributed module a census subject marker; never raise the baseline.

## Acceptance Criteria

- [ ] **AC1** Given main after this fix, then `test_test_census.py` passes whole: no test module holds an unmarked literal list of three or more script names, and the unattributed count is at or below the declared baseline, which is not raised; raising the baseline or deleting the mirror scan to go green fails it
  - **Verify:** pytest tools/tests/test_test_census.py
- [ ] **AC2** Given `test_lean_lane_history.py` still proves what US0931's criteria say, then its three Verify selectors still pass
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_lane_history.py

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-25 | sdlc-studio | Filed |
| 2026-09-25 | Claude Opus 5.5 | Criteria authored with Verify lines; joined the Sprint 4 batch because it blocks the push |
