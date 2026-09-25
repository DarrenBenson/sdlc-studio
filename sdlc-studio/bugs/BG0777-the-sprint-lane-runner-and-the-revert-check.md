# BG0777: The sprint lane runner and the revert check run only a criterion's first Verify line

> **Status:** Open
> **Severity:** Medium
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/verify_ac.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_verify_ac.py
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

- [ ] **AC1** The behaviour described is corrected: After BG0687, `verify_ac` run executes every Verify line under a criterion, but `sprint.lane_verify` and `lane_return` (sprint.py ~2503, ~2774) and...
- [ ] **AC2** The proposed fix lands, pinned by a test: Route both through ACBlock.verifiers so every line runs, as `verify_story` does, with a stacked-block test each.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-25 | sdlc-studio | Filed |
