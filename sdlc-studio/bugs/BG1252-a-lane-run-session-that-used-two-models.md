# BG1252: A lane run session that used two models is priced entirely at the rate of the model with the most tokens

> **Status:** Open
> **Severity:** Medium
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/lib/harness_usage.py, .claude/skills/sdlc-studio/scripts/lib/lanes.py, .claude/skills/sdlc-studio/scripts/lib/run_state.py, .claude/skills/sdlc-studio/reference-sprint.md, .claude/skills/sdlc-studio/scripts/tests/test_harness_usage.py, .claude/skills/sdlc-studio/scripts/tests/test_lane_run.py, changelog.d/BG1252.md
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

- [ ] **AC1** Given a CLI output whose usage names two models, when `harness_usage.parse` reads it, then the `Usage` carries a per-model split whose components sum to the session's counts. Fails on: the split dropped so only `_largest`'s model survives.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_harness_usage.py::HarnessUsageTests::test_a_two_model_session_carries_its_split
- [ ] **AC2** Given `sprint.py lane run` with a fake CLI whose usage names two models, then `sprint.py lane return`, then the unit's dollars equal each model's components priced at its own rate (the $0.4358 shape, not $0.5425), and `reference-sprint.md#dollar-cost` no longer says a session is priced at its largest model. Fails on: the lane record or `run_reading` carrying no `by_model`, so `record_delegated_tokens` books the whole session under one model.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lane_run.py::LaneRunTests::test_a_two_model_session_is_priced_per_model
- [ ] **AC3** Given a single-model session, or a lane record written before the fix with no split, when it is returned, then it prices exactly as before under its one named model. Fails on: a record without a split read as unpriced or as zero.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lane_run.py::LaneRunTests::test_a_record_without_a_split_prices_at_its_one_model

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-06 | Claude Opus 5.5 | Filed |
| 2026-11-06 | Claude Opus 5.5 | Groomed for run eight (D0416): criteria with Verify checks, Points and Affects |
