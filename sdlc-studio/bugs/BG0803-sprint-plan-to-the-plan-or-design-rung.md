# BG0803: sprint plan to the plan or design rung crashes in capacity_report on the default token budget

> **Status:** In Progress
> **Created:** 2026-09-27
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py, changelog.d/BG0803.md
> **Severity:** Low
> **Points:** 1

## Summary

CR0592 bullet (file line 25) re-measured at f76b70cc: on a fresh v6 project `sprint.py plan --bugs inbox --goal design` (and `--goal plan`) raises `TypeError: '>' not supported between NoneType and int` at sprint.py:628 (`high > token_budget`); a non-build rung leaves the forecast unpriced and the default 500,000 budget is always set.

## Steps to Reproduce

init run; file one groomed bug; sprint.py plan --bugs inbox --goal design.

## Proposed Fix

Read an unpriced forecast as unjudged against the token budget.

## Acceptance Criteria

- [ ] **AC1** Given a batch whose forecast carries no token figure (goal `plan` or `design`) under the default 500,000 token budget, when `capacity_report` runs, then `tokens_may_exceed` is False and the token half reads unjudged. Fails on: `high > token_budget` with `high` None (HEAD TypeError)
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::CapacityHonestyTests::test_an_unpriced_forecast_under_a_token_budget_is_not_compared
- [ ] **AC2** Given a fresh `init` project with one groomed bug, when `sprint.py plan --bugs inbox --goal design` runs through the CLI, then it exits 0 and prints `batch: 1 unit(s)`. Fails on: a guard in `build_plan` that another caller of capacity_report bypasses
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::CapacityHonestyTests::test_a_design_rung_plan_on_a_fresh_project_exits_zero

## Notes

First-week: a traceback and no plan. Mint from CR0592 (BG0731 pattern) and remove the bullet there.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-27 | sdlc-studio | Created via `new` (deterministic) |
| 2026-09-27 | sdlc-studio v6 planning | Created for v6.0.0 Sprint 6 from the seat planning (BG0803) |
