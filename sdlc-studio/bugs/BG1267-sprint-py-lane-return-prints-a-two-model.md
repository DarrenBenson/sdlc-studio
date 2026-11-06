# BG1267: `sprint.py lane return` prints a two-model session's `lane run cost` at the largest model's rate, and BG1244's fragment misstates what the parser did before

> **Status:** Open
> **Severity:** Low
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, changelog.d/BG1244.md, .claude/skills/sdlc-studio/scripts/tests/test_lane_run.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py
> **Evidence:** run eight (RUN-01M6RZQZ) BG1252 review round 1 ([pre-existing]) and BG1244 review round 1 ([new]), and the orchestrator's friction log (R8-F7)
> **Created:** 2026-11-06
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-06T20:38:19Z

## Summary

`sprint.py lane return` prices its printed line with `prices.cost(reading["model"], reading["components"], prices.load(root))` (`.claude/skills/sdlc-studio/scripts/sprint.py:8659`, shipped by US1126 in `2c8d0c40`), which never reads the `by_model` breakdown BG1252 added to the reading, so a two-model session prints US$0.0047 while the report prices the unit per model at US$0.0501. The report's unit dollars are right; the line the operator reads at return contradicts them. BG1252's reviewer found it outside BG1252's `Affects`. From BG1244's review: `changelog.d/BG1244.md:9-10` says a `modelUsage` array was formerly read as absent, which holds only for an empty one: a non-empty array such as AC1's `[1]` raised at the base (`lib/harness_usage.py:181` at `fd1c2b5b`).

## Steps to Reproduce

Return a lane whose fake CLI reports usage for two models (BG1252's fixture) and compare the `lane run cost` line with the unit's dollars on the sprint report: the line prices every token at the largest model. For the fragment, run `harness_usage.parse` at `fd1c2b5b` on a `modelUsage` of `[1]`: it raises.

## Proposed Fix

Price the printed line from the reading's `by_model` when present, through the same call the report uses, naming each model or 'mixed', and assert in `test_lane_run.py` that the line's figure equals the report's; reword the BG1244 fragment to say an empty array was read as absent and a non-empty one raised.

## Acceptance Criteria

- [ ] **AC1** The behaviour described is corrected: `sprint.py lane return` prices its printed line with `prices.cost(reading["model"], reading["components"], prices.load(root))`...
- [ ] **AC2** Following the recorded steps no longer reproduces the defect: Return a lane whose fake CLI reports usage for two models (BG1252's fixture) and compare the `lane run cost` line with the unit's dollars on the sprint report...
- [ ] **AC3** The proposed fix lands, pinned by a test: Price the printed line from the reading's `by_model` when present, through the same call the report uses, naming each model or 'mixed', and assert in...

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-06 | Claude Opus 5.5 | Filed |
