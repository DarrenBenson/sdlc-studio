# BG1186: The release verify lane's declared budget is 600 s against a measured 3,340 s, so every release run prints OVER and the pin keeps it there

> **Status:** Open
> **Severity:** Low
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/scripts/gate.py, .claude/skills/sdlc-studio/scripts/tests/test_gate.py, changelog.d/BG1186.md
> **Evidence:** US1112 builder report, release verify lane measured at 3,340 s (2026-11-03).
> **Created:** 2026-11-03
> **Created-by:** sdlc-studio file
> **Raised-by:** claude; human; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-03T03:24:21Z

## Summary

2026-11-03, US1112's build (run five). `VERIFY_LANE_BUDGET_S = 600` (gate.py:1641) and `test_gate.py::ReleaseGateCostTests::test_the_release_gate_completes_within_its_declared_budget` asserts it is at most 600. US1112's builder measured the release verify lane at 3,340 s on 8 cores with its working batch, so the lane prints 'OVER the 600s declared budget' on every release run. A clause that is always printed tells the reader nothing, and the pin forbids the honest figure.

## Steps to Reproduce

1. `grep -n VERIFY_LANE_BUDGET_S .claude/skills/sdlc-studio/scripts/gate.py .claude/skills/sdlc-studio/scripts/tests/test_gate.py`.
2. Run the release verify lane (`gate._verify_acs(root, batch=True)`): its detail ends with the OVER clause.

## Proposed Fix

After US1113 lands, re-derive the budget from the measured lane on this repository, and pin it to that measurement with a margin rather than to a ceiling no run meets.

## Acceptance Criteria

- [ ] **AC1** `VERIFY_LANE_BUDGET_S` states the release verify lane's measured wall-clock on this repository after US1113 with its margin, and the test pins it to that figure, not to 600.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_gate.py::ReleaseGateCostTests::test_the_release_gate_completes_within_its_declared_budget

## Impact

The release gate's cost line always reads over budget, so a real cost regression is indistinguishable from the normal run.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-03 | claude | Filed |
