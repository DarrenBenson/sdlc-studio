# BG0860: A sprint plan preview with no --write appends forecast rows to the tracked evidence log, so each dry run adds a duplicate forecast per unit

> **Status:** Fixed
> **Severity:** Medium
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py, changelog.d/BG0860.md
> **Evidence:** sdlc-studio/retros/evidence/forecasts-2026-09-30.jsonl, committed in 04325bdd: nine rows from three previews and the write
> **Created:** 2026-09-30
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-09-30T11:53:29Z

## Summary

> **Groomed:** 2026-10-01 (D0291) - premise reproduced at HEAD: on a fixture, a preview at 3 points then a preview after regrooming to 5 left two rows (points 3, 5); `plan --write` added none, and `telemetry.forecasts` reads US0001 at 3 points - the retro judges the stale preview.

Planning RUN-01M3RPSK (2026-09-30), three `sprint.py plan --worklist ...` previews without --write each printed 'forecast recorded: N unit(s) at plan time' and appended rows to sdlc-studio/retros/evidence/forecasts-2026-09-30.jsonl, a tracked file; BG0852 holds two rows (3 points from a preview, then 5 after regrooming) before the run was opened. A preview should write nothing, and the retro 'judges THIS number' - so which forecast the run is judged against depends on how many previews ran, the duplicate-row shape that made a stale row win a join before (mutation ledger).

## Steps to Reproduce

Run `sprint.py plan --worklist <file>` (no --write) twice on the same batch, then `wc -l sdlc-studio/retros/evidence/forecasts-$(date +%F).jsonl`: rows are added per run, per unit.

## Proposed Fix

Record the forecast only when --write opens the run (`record_forecast` call at sprint.py:9844 moves under `if write:`; the rolling-cycle caller already runs inside an opened run); a preview prints the forecast without persisting it. A deletion of writes, and of the 'Unconditional' rationale comment. `PointsForecastTests::test_the_recorded_forecast_carries_the_points_it_was_made_from` passes `--write`.

## Acceptance Criteria

- [ ] **AC1** Given a fixture with one Ready unit at 3 points, when `sprint.py plan --worklist <file>` runs without --write, the unit is regroomed to 5 points, and `sprint.py plan --worklist <file> --write` runs, then no forecasts-*.jsonl row exists after the preview and `telemetry.forecasts` reads the unit at 5 points after the write. Fails on: HEAD, which writes the preview's row and reads 3 points (first record wins)
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::PointsForecastTests::test_a_preview_writes_no_forecast_row
  - **Verified:** yes (2026-10-01)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-30 | sdlc-studio | Filed |
| 2026-10-01 | backlog value pass (D0291) | Groomed: premise executed at HEAD (stale preview row wins the read); AC adds the regroom arm; Verify moved to the existing PointsForecastTests class; Points 2 kept |
