# BG1252: A lane run session that used two models is priced entirely at the rate of the model with the most tokens

> **Status:** Open
> **Severity:** Medium
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/lib/lanes.py, .claude/skills/sdlc-studio/scripts/lib/harness_usage.py, .claude/skills/sdlc-studio/scripts/lib/run_state.py, .claude/skills/sdlc-studio/scripts/tests/test_lane_run.py, .claude/skills/sdlc-studio/scripts/tests/test_harness_usage.py, .claude/skills/sdlc-studio/scripts/tests/test_run_state.py
> **Evidence:** run seven (RUN-01M6RAP7) US1123 review round 2
> **Created:** 2026-11-06
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-06T14:58:26Z

## Summary

`lib/lanes.py` keeps one model per lane session record, and `run_state.record_delegated_tokens` (about `run_state.py:2610-2613`) prices the whole session at that model's rate. In US1123's round-2 probe a two-model session read $0.5425 against $0.4358 priced per model (+24%), and nothing on the row says so; the reference documents the rule.

## Steps to Reproduce

Run `sprint.py lane run` with a fake CLI whose usage names two models, then `sprint.py lane return`, and compare the row's dollars with each model's components priced separately.

## Proposed Fix

Carry the per-model split from `lib/harness_usage.py` through the lane session record and price each model's components at its own rate; pin it with a two-model fixture.

## Acceptance Criteria

- [ ] **AC1** The behaviour described is corrected: `lib/lanes.py` keeps one model per lane session record, and `run_state.record_delegated_tokens` (about `run_state.py:2610-2613`) prices the whole session at...
- [ ] **AC2** Following the recorded steps no longer reproduces the defect: Run `sprint.py lane run` with a fake CLI whose usage names two models, then `sprint.py lane return`, and compare the row's dollars with each model's components...
- [ ] **AC3** The proposed fix lands, pinned by a test: Carry the per-model split from `lib/harness_usage.py` through the lane session record and price each model's components at its own rate; pin it with a...

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-06 | Claude Opus 5.5 | Filed |
