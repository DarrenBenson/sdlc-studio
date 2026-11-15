# CR-0703: Fit the plan's dollar forecast from measured dollars per point, not priced tokens times the input price

> **Status:** Proposed
> **Parent:** CR0694
> **Priority:** Medium
> **Type:** enhancement
> **Size:** S
> **Affects:** .claude/skills/sdlc-studio/scripts/lib/run_state.py, .claude/skills/sdlc-studio/scripts/retro.py, .claude/skills/sdlc-studio/scripts/tests/test_dollar_rate_fit.py, .claude/skills/sdlc-studio/scripts/tests/test_run_state.py, .claude/skills/sdlc-studio/scripts/tests/test_retro.py
> **Evidence:** Run twelve (RUN-01M7E52T) US1150 builder hand-back; RPT0030's measured $111.66 over 41.4M priced tokens
> **Date:** 2026-11-15
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5 (run twelve orchestrator); agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-15T01:16:21Z

## Summary

US1150 forecasts dollars as the priced forecast times the planned model's input price per million, as decision D0476 ruled. Priced tokens weight cache reads at 0.1 of input, but claude-opus-5-5's cache reads cost less than that in the price table, so the formula runs high: RPT0030 works out to about $2.69 per million priced tokens against a $4 input price, about 49% high. A rate fitted from the measured runs' dollars per point (the median of the last five priced runs, the way the priced rate is fitted) would forecast what the report measures.

## Impact

Serves Abena Osei's End goal 3 (cost you can predict). The dollar row's ratio would read about 1.0 instead of about 0.67 on a typical run.

## Acceptance Criteria

- [ ] The plan's dollar forecast comes from measured dollars per point over the recent priced runs, naming the runs it was fitted from, and falls back to priced times the input price only when fewer than three runs carry a dollar figure, saying so.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-15 | Claude Opus 5.5 (run twelve orchestrator) | Raised |
