# BG1150: sprint.py still says the planner reads the series 'the budget lane reads', though that lane was deleted in 315ec358

> **Status:** Open
> **Severity:** Low
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, changelog.d/BG1150.md, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py
> **Evidence:** US1107 APPROVE round 2 by qa-seat-US1107-r1 (brief 1fb837375bed), [pre-existing] finding; 315ec358.
> **Created:** 2026-11-01
> **Created-by:** sdlc-studio file
> **Raised-by:** claude; human; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-01T03:45:04Z

## Summary

qa-seat-US1107-r1 (2026-11-01) found that the budget lane BG0415 named, `tools/gate_timing.py budget`, was removed in 315ec358 (US0880, 2026-09-24). Three sprint.py strings outlived it: the comment at :12751-12752 ('The planner reads the SAME file the budget lane reads'), :12763 ('exactly as the budget lane does'), and the printed basis at :12837 ('the same series the budget lane reads'), which a plan shows the operator. Today the per-commit budget line in .githooks/commit-msg (:417 and :423-429) writes the series the planner reads and checks the live figure; it does not read the series. A lesson reason in this run (L-0268) repeated the stale string.

## Steps to Reproduce

1. `git show 315ec358 -- tools/gate_timing.py | grep -n cmd_budget`: the lane is removed.
2. `grep -n 'budget lane' .claude/skills/sdlc-studio/scripts/sprint.py`: three sites.
3. `sprint.py plan` prints the :12837 basis string.

## Proposed Fix

Reword the three strings to name what holds today: the series that .githooks/commit-msg records each commit (commit-msg:417), which the planner reads.

## Acceptance Criteria

- [ ] **AC1** No string in sprint.py names a budget lane reading the gate-timings series, and the printed cost basis names the commit hook's record as its source.
  - **Verify:** shell ! grep -n 'budget lane reads' .claude/skills/sdlc-studio/scripts/sprint.py

## Impact

A plan's printed cost basis and two comments describe a lane that no longer exists, and readers quote them as fact (LC-018).

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-01 | claude | Filed |
