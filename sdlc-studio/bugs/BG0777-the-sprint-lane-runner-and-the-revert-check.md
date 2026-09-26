# BG0777: The sprint lane runner and the revert check run only a criterion's first Verify line

> **Status:** Fixed
> **Severity:** Medium
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/verify_ac.py, .claude/skills/sdlc-studio/scripts/tests/test_lean_lane_every_line.py, changelog.d/BG0777.md
> **Created:** 2026-09-25
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-09-25T18:24:35Z

## Summary

After BG0687, `verify_ac` run executes every Verify line under a criterion, but `sprint.lane_verify` and `lane_return` (sprint.py ~2503, ~2774) and `verify_ac`'s revert check (~3966, ~4033) still run only the first. On a stacked block with the second line red, `verify_ac` run reports fail=1 while `lane_return` reports outcome=fixed. Found by BG0687's QA review; no stacked block exists in this corpus, but a consuming project may write one.

## Steps to Reproduce

1. Author a criterion with two Verify lines, the second red. 2. `verify_ac` run reports fail=1. 3. sprint lane return on the same unit reports outcome=fixed.

## Proposed Fix

Route both through ACBlock.verifiers so every line runs, as `verify_story` does, with a stacked-block test each.

## Acceptance Criteria

- [ ] **AC1** Given a unit whose criterion carries two Verify lines, the first green and the second red, when `sprint.py lane return` records its outcome, then the outcome is not `fixed` and the red line is named, as `verify_ac run` reports it. Fails on: `lane_verify`/`lane_return` running only `block.verifier`
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_lane_every_line.py::LaneEveryLineTests::test_a_red_second_line_is_not_fixed_on_lane_return
  - **Verified:** yes (2026-09-26)
- [ ] **AC2** Given the same stacked criterion, when `verify_ac`'s revert check runs it against the base, then every Verify line is run on both sides, so a second line that passes at base as well is caught. Fails on: the revert check reading only the first line
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_lane_every_line.py::LaneEveryLineTests::test_the_revert_check_runs_every_line
  - **Verified:** yes (2026-09-26)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-25 | sdlc-studio | Filed |
| 2026-09-25 | sdlc | Groomed for Sprint 5: criteria and Verify selectors written |
