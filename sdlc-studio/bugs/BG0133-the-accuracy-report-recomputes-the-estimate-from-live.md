# BG0133: The accuracy report recomputes the estimate from live constants, so it cannot falsify the estimator

> **Status:** Open
> **Severity:** High
> **Effort:** M
> **Created:** 2026-07-14
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1

## Summary

retro.py accuracy derives each unit estimate at retro time from the current `sprint.BASE_TOKEN_BUDGET` and `TOKENS_PER_COGNITIVE`, instead of reading a forecast recorded when the sprint was planned. The estimate is a function of todays code, not of what the planner actually predicted, so the measurement loop cannot falsify its own estimator: recalibrate the constants and every past sprint is retroactively deemed to have estimated something else. The ratio always drifts toward 1.0x and the velocity history stops being evidence. An estimator changed mid-sprint rewrites its own baseline - CR0257 added the effort-proxy seed during the very sprint whose accuracy is being measured. Separately, reporting a 1.09x fit against the same six units the constants were fitted to is in-sample training error, not validation, and must not be read as independent confirmation.

## Steps to Reproduce

1. Note RETRO0024 as written: BG0126 was forecast at 245,000 tokens against an actual 46,792 - a 5.2x over-estimate, and the entire evidence that drove the recalibration of `TOKENS_PER_COGNITIVE` from 5,000 to 600. 2. Run: python3 .claude/skills/sdlc-studio/scripts/retro.py accuracy --id RETRO0024. 3. Observe the same unit now reports est=73,400, actual=46,792, 1.57x. The 5.2x miss has been erased from the record by the change it caused. 4. Also observe sdlc-studio/.local/sprint-plan.json holds a stale batch dated 2026-07-10 (BG0076, CR0202...), because sprint plan only persists it under --write - so for the current sprint no plan-time forecast exists on disk to compare against at all.

## Proposed Fix

sprint plan must RECORD its per-unit token forecast, and the constants that produced it, at plan time (persist unconditionally, not only under --write, or make the close read the run state). retro.py accuracy must READ that recorded number and never re-derive it; a unit whose plan-time forecast was never recorded is UNFORECAST and excluded from the ratio, exactly as an unmeasured unit is - silence on the estimate side is not evidence either. A forecast regenerated at judgement time is not a prediction.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-14 | sdlc-studio | Filed |
