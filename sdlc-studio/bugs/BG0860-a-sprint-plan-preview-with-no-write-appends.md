# BG0860: A sprint plan preview with no --write appends forecast rows to the tracked evidence log, so each dry run adds a duplicate forecast per unit

> **Status:** Open
> **Severity:** Medium
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py,.claude/skills/sdlc-studio/scripts/tests/test_sprint.py, changelog.d/BG0860.md
> **Evidence:** sdlc-studio/retros/evidence/forecasts-2026-09-30.jsonl, committed in 04325bdd: nine rows from three previews and the write
> **Created:** 2026-09-30
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-09-30T11:53:29Z

## Summary

Planning RUN-01M3RPSK (2026-09-30), three `sprint.py plan --worklist ...` previews without --write each printed 'forecast recorded: N unit(s) at plan time' and appended rows to sdlc-studio/retros/evidence/forecasts-2026-09-30.jsonl, a tracked file; BG0852 holds two rows (3 points from a preview, then 5 after regrooming) before the run was opened. A preview should write nothing, and the retro 'judges THIS number' - so which forecast the run is judged against depends on how many previews ran, the duplicate-row shape that made a stale row win a join before (mutation ledger).

## Steps to Reproduce

Run `sprint.py plan --worklist <file>` (no --write) twice on the same batch, then `wc -l sdlc-studio/retros/evidence/forecasts-$(date +%F).jsonl`: rows are added per run, per unit.

## Proposed Fix

Record the forecast only when --write opens the run; a preview prints the forecast without persisting it.

## Acceptance Criteria

- [ ] **AC1** Given a clean evidence directory, when `sprint.py plan --worklist <file>` runs without --write, then no forecasts-*.jsonl row is written. Fails on: HEAD, which appends one row per unit per preview
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::PlanForecastTests::test_a_preview_writes_no_forecast_row

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-30 | sdlc-studio | Filed |
