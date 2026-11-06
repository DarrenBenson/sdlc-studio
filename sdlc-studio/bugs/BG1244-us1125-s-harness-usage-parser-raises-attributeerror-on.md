# BG1244: US1125's harness usage parser raises `AttributeError` on a usage container that is not an object, and three of its rules are unpinned

> **Status:** Open
> **Severity:** Low
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/lib/harness_usage.py, .claude/skills/sdlc-studio/scripts/tests/test_harness_usage.py
> **Evidence:** run seven (RUN-01M6RAP7) US1125 review round 1
> **Created:** 2026-11-06
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-06T14:36:13Z

## Summary

Run seven, US1125 round 1 (APPROVE, non-blocking). (1) A JSON-valid line whose usage container is not an object raises `AttributeError` out of `parse()` instead of returning unmetered: Claude `modelUsage` `{"m": 5}` or `[1]` and `usage` `"x"` (`harness_usage.py:181`, :191), Copilot `modelMetrics` entry `"x"`, `data` `[1]` and a `tokenDetails` entry 4 (:275, :281, :292), OpenCode `part` `"x"` and `cache` `[1]` (:304, :309). All eight crash, while the Cursor and Codex readers treat the same shape as no usage (:234, :246) and the docstring (:48) says a count that is not one is unmetered. No captured CLI emits such a shape. (2) The rule that an absent reasoning count is None and named in `unreported`, never zero (:16), has no test through `_opt`: returning 0 for a missing key at :134 passes the module (6 tests, 20 subtests). (3) `_largest` (:337-339), the model that carried the most tokens, is unpinned: returning the first model passes, every capture being single-model. (4) The docstring at :31 says Codex's `input_tokens` holds `cached_input_tokens`, observed from "14524 input with 12288 cached", which fits either reading; the claim is true, but the deciding evidence, the rollout's `total_tokens` 14529 equalling input plus output, is not named.

## Steps to Reproduce

Call `harness_usage.parse` on a Claude line whose `modelUsage` is `[1]`: it raises `AttributeError`. Apply the `_opt` and `_largest` mutants in a scratch copy and run `pytest .claude/skills/sdlc-studio/scripts/tests/test_harness_usage.py`: all pass.

## Proposed Fix

Check each container's type before reading it and return unmetered with a reason, as the Cursor and Codex readers do, with the eight shapes as subtests. Add a capture with the reasoning field removed and a two-model capture asserting `_largest`. Name the `total_tokens` evidence in the Codex docstring.

## Acceptance Criteria

- [ ] **AC1** The behaviour described is corrected: Run seven, US1125 round 1 (APPROVE, non-blocking).
- [ ] **AC2** Following the recorded steps no longer reproduces the defect: Call `harness_usage.parse` on a Claude line whose `modelUsage` is `[1]`: it raises `AttributeError`.
- [ ] **AC3** The proposed fix lands, pinned by a test: Check each container's type before reading it and return unmetered with a reason, as the Cursor and Codex readers do, with the eight shapes as subtests.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-06 | Claude Opus 5.5 | Filed |
