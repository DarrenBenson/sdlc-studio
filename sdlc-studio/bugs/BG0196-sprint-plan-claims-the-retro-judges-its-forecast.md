# BG0196: sprint plan claims the retro judges its forecast, but accuracy cannot read an aggregate-only forecast

> **Status:** Open
> **Severity:** Medium
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/retro.py
> **Created:** 2026-07-18
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1

## Summary

sprint plan --write prints 'forecast recorded: N unit(s) at plan time ... The retro judges THIS number - it never re-derives one' and stores an aggregate in run-state as `token_forecast.` retro accuracy does not read that key: it judges PER-UNIT forecast telemetry records, which only a runner-driven sprint writes. An interactive sprint therefore records a forecast the retro reports as UNFORECAST ('no plan-time forecast was recorded'), so the two halves of the estimate loop contradict each other. Observed at RUN-01KXT0YV: run-state carried `token_forecast`=650000 while accuracy reported UNFORECAST for all 9 units. Distinct from CR0278, which covers the ACTUALS side.

## Steps to Reproduce

1. Run sprint.py plan --write on an interactive sprint; note the 'forecast recorded' line and `token_forecast` in .local/run-state.json. 2. Close the sprint and run retro.py accuracy --id RETROxxxx --write. 3. Observe 'UNFORECAST: no plan-time forecast was recorded, so there is no prediction to judge' despite the value being present in run-state.

## Proposed Fix

Either have accuracy fall back to run-state's aggregate `token_forecast` when no per-unit forecast telemetry exists (reporting a sprint-level rather than per-unit ratio, clearly labelled), or correct the plan's message so it does not promise a judgement the retro cannot perform for an interactive run. The first is preferable: the aggregate is a real plan-time prediction and judging it is the point of the loop.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-18 | sdlc-studio | Filed |
