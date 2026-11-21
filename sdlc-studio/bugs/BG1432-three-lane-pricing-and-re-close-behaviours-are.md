# BG1432: Three lane-pricing and re-close behaviours are pinned by no test: each split share's per-model split, the minutes split, and the lane-yield re-freeze over a kept window

> **Status:** Won't Fix
> **Severity:** Low
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_lane_split_pins.py, changelog.d/BG1432.md, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py
> **Evidence:** Run twelve (RUN-01M7E52T) reviews: qa-seat-BG1397-r1 sdlc-studio/reviews/verdicts/BG1397/6046186d7479-e8e32331.txt and qa-seat-BG1394-r1 sdlc-studio/reviews/verdicts/BG1394/c917b53aa77c-a8dbb4d3.txt ([new], non-blocking)
> **Created:** 2026-11-15
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5 (run twelve orchestrator); agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-15T01:11:02Z

## Summary

Run twelve's BG1397 and BG1394 reviews found three correct behaviours at 93db614d that no test pins: a mutant leaving each unit's by-model split whole (sprint.py:8639) survives, and would count a lane's dollars once per unit; a mutant giving every unit the whole `--minutes` (sprint.py:8642) survives; and deleting the lane-yield re-freeze over the kept window on a re-close with an unreadable meter (sprint.py:10242) survives, since the fixture holds no refusal log or git history. The `_lane_agent_totals` docstring also still describes the old refusal of a multi-unit total.

## Steps to Reproduce

Apply each of the three mutants named in the summary and run `test_multi_unit_lane_split.py`, `test_lane_land.py`, `test_lean_lane_delegated_tokens.py` and `test_re_close_unreadable_meter.py`: each mutant survives.

## Proposed Fix

Add tests that read each share's by-model components and minutes after a three-unit split with unequal points, and a re-close fixture with a git root and refusals logged either side of the kept window; correct the `_lane_agent_totals` docstring.

## Acceptance Criteria

- [ ] **AC1** Given a three-unit lane with unequal points and one builder total carrying a by-model split and minutes, when it is returned, then each unit's by-model components and minutes are its share, summing to the whole. Fails on: any unit holding the whole split or the whole minutes.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lane_split_pins.py::SplitShareTests
- [ ] **AC2** Given a reopened run whose meter cannot be read at the second close, with refusals logged before and after the kept window, when the close runs, then the lane-yield appendix counts only the refusals inside the kept window. Fails on: post-reopen refusals counted.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lane_split_pins.py::ReFreezeTests

## Resolution

Won't Fix under D0564: the operator approved the product seat's proposal (D0562) because only a test or pin is missing on behaviour that is right on every path a user reaches. Lane pricing and re-close are correct by execution; only mutation-survival pins and a stale docstring remain. The qa re-check at 81e02369 found the defect still present (D0563), so this closes it as not worth its cost, not as fixed.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-15 | Claude Opus 5.5 (run twelve orchestrator) | Filed |
| 2026-11-21 | Claude Opus 5.5 (product seat, delegate under D0545) | Won't Fix under D0564: the operator approved the product seat's list (D0562); reason in Resolution |
