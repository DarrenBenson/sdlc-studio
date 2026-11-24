# BG1398: The tool-call budget in a multi-unit lane brief is printed once per unit and nothing states the lane's total

> **Status:** Fixed
> **Severity:** Low
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_lane_total_budget.py, changelog.d/BG1398.md
> **Evidence:** RUN-01M78TKD, 2026-11-13: orchestrator
> **Created:** 2026-11-13
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5 (run eleven orchestrator); agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-13T01:11:20Z

## Summary

`_lane_budget_line` (sprint.py, called from `_lane_builder_commands` at the end of each `lane_brief_text`) prints one `Budget: N tool calls` line inside each unit's brief, and `cmd_lane` prints the briefs one after another with nothing after them, so a builder handed a multi-unit lane never sees the lane's sum.

Reproduced at cecc9dfe7 (2026-11-24): `sprint lane brief --units US0101 US0102` over the `test_lane_brief_budget.py` fixture (1 and 5 points) prints `Budget: 38 tool calls` and `Budget: 90 tool calls` and no total.

## Steps to Reproduce

1. Open a run whose batch holds two Ready units of 1 and 5 points.
2. Run `sprint.py lane brief --units US0101 US0102`.
3. Two per-unit `Budget:` lines are printed; no line states the lane's 128 tool calls.

## Proposed Fix

After the text briefs, when more than one unit is briefed, print one line stating the lane's total: the sum of the per-unit budgets (`lane_call_budget` of each unit's Points) and the unit count. When any briefed unit declares no Points, the line says no total is derived and names the unsized unit, rather than summing the sized ones. A brief of one unit prints no separate total, and the total line must not match the `Budget: N tool calls` form the single-unit tests count.

## Acceptance Criteria

- [ ] **AC1** Given an open run whose batch holds two Ready units of 1 and 5 points, when `sprint lane brief --units` names both, then the output states the lane's total once, after both briefs, as 128 tool calls over 2 units (38 + 90). Fails on: two per-unit `Budget:` lines and no total.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lane_total_budget.py::LaneTotalBudgetTests::test_a_multi_unit_brief_states_the_lane_total_once
  - **Verified:** yes (2026-11-24)
- [ ] **AC2** Given the same run, when `sprint lane brief --units` names one unit, then no lane-total line is printed and the brief still carries exactly one `Budget: N tool calls` line. Fails on: a mutant printing a total for a lane of one unit, which repeats its budget as a second figure.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lane_total_budget.py::LaneTotalBudgetTests::test_a_single_unit_brief_states_no_separate_total
  - **Verified:** yes (2026-11-24)
- [ ] **AC3** Given a two-unit lane in which one unit declares no Points, when the brief is printed, then the total line says no lane total is derived and names that unit, and states no number. Fails on: no statement at all, or a mutant summing only the sized unit and understating the lane.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lane_total_budget.py::LaneTotalBudgetTests::test_an_unsized_unit_leaves_the_lane_total_underived
  - **Verified:** yes (2026-11-24)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-13 | Claude Opus 5.5 (run eleven orchestrator) | Filed |
| 2026-11-24 | Sam Eriksson (qa) | Groomed for run twenty-five: reproduced at cecc9dfe7; stale line reference replaced; Steps and Proposed Fix made concrete; three executable criteria (the total, the one-unit boundary, the unsized unit); Affects drops test_lane_brief_budget.py and test_sprint.py |
