# CR-0602: A run's token and minute actuals are measured without the operator stamping a baseline

> **Status:** Proposed
> **Priority:** Medium
> **Type:** Improvement
> **Size:** M
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/lib/run_state.py, .claude/skills/sdlc-studio/scripts/sprint_report.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_run_state.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py
> **Evidence:** eval 09 v6-main RPT0001 appendix `Tokens by model: NOT MEASURED`; decisions.md D0280
> **Date:** 2026-09-28
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-09-28T16:27:08Z

## Summary

Eval 09's report read tokens NOT MEASURED (no session baseline at plan time) and minutes NOT MEASURED despite a wall-clock actual, because no minutes forecast was recorded. D0280 names automatic token capture as Sprint 7 / v6.1 work; no artefact carries it.

## Impact

Every consuming project: the report's cost and accuracy rows are NOT MEASURED unless the operator knows to stamp them.

## Acceptance Criteria

- [ ] Given `sprint plan --write`, then the run records a session token baseline and a minutes forecast without an extra command, and the close's report measures both

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-28 | sdlc-studio | Raised |
