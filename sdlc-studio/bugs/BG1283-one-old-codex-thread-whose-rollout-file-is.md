# BG1283: One old Codex thread whose rollout file is gone makes every later Codex reading in that workspace unmetered, permanently

> **Status:** Open
> **Severity:** Low
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/lib/meter_codex.py, .claude/skills/sdlc-studio/scripts/tests/test_meter_codex.py, changelog.d/BG1283.md
> **Evidence:** the between-releases review before v6.3.0 (D0427, LL0005), code leg A; repro under scratchpad rel63/legs/scratch-a/
> **Created:** 2026-11-08
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-08T13:07:10Z

## Summary

Every Codex reading folds every workspace thread ever recorded. One old thread whose rollout file was pruned or moved therefore makes every later reading in that workspace tokens None, permanently, though that thread is no part of any later run. Each reading also re-reads every historical rollout in full.

## Steps to Reproduce

by reading: `_usage` returns 'is missing' and read() returns none(...) for any thread with `tokens_used` truthy (not executed).

## Proposed Fix

Skip and count a thread whose rollout is missing and which has not changed since the run opened (or since the previous stamp), and name it in the basis.

## Acceptance Criteria

- [ ] **AC1** Given a Codex store whose workspace holds one live thread and one old thread that spent tokens, whose rollout file has since been removed and which has not changed since the run opened, when the Codex meter reads the workspace, then the reading carries the live thread's tokens and components, not tokens None. Fails on: one pruned rollout making every later reading in the workspace unmetered.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_meter_codex.py::CodexMeterTests::test_an_old_thread_whose_rollout_is_gone_is_skipped_and_the_rest_is_read
- [ ] **AC2** Given that same store, when the meter reads it, then the reading's basis says how many threads were skipped for a missing rollout and names each by its thread id, and its `threads` count leaves them out. Fails on: a thread dropped from the sum with nothing on the page saying so.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_meter_codex.py::CodexMeterTests::test_the_basis_names_each_thread_skipped_for_a_missing_rollout
- [ ] **AC3** Given a thread that spent tokens after the run opened and whose rollout file is missing, when the meter reads the workspace, then the reading is tokens None with a reason naming that thread and its rollout, as it is today. Fails on: this run's own spend skipped as if it were an old thread's.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_meter_codex.py::CodexMeterTests::test_a_thread_that_spent_in_this_run_with_no_rollout_is_still_unmetered

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-08 | Claude Opus 5.5 | Filed |
