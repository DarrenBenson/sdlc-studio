# CR-0668: The token meter recognises a Codex CLI run and reads its token actual from the Codex store

> **Status:** Proposed
> **Parent:** RFC0062
> **Priority:** Medium
> **Type:** Feature
> **Size:** M
> **Affects:** .claude/skills/sdlc-studio/scripts/lib/token_meters.py, .claude/skills/sdlc-studio/scripts/lib/run_state.py, .claude/skills/sdlc-studio/scripts/tests/test_token_meters.py, .claude/skills/sdlc-studio/scripts/tests/test_run_state.py
> **Evidence:** RFC0062 Phase 1; run six's transcripts and the 2026-11-06 capture of one headless session per CLI harness.
> **Date:** 2026-11-06
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-06T11:17:50Z

## Summary

`token_meters.HARNESSES` names claude, cursor, copilot and opencode; Codex CLI is not recognised, so a sprint driven from Codex records no token actual. Codex CLI 0.160 keeps its threads in SQLite under ~/.codex (`state_5.sqlite`, `thread_history_1.sqlite)`, not in the rollout JSONL files older versions wrote.

## Impact

Every sprint report and velocity row for a project driven from Codex CLI.

## Acceptance Criteria

- [ ] When the running harness is Codex CLI, the close records that run's token total from Codex's own store, counting input, output and cache write with cache reads apart, and with cached input split out of input
- [ ] The Codex reader is chosen by `SDLC_STUDIO_HARNESS`=codex or by an environment variable a real Codex session sets, established from a captured session
- [ ] A missing, locked or unreadable store records no total and names why; the store is only ever opened read-only
- [ ] The reader's tests use a fixture taken from a real captured Codex session

## Recommendation

A lib/`meter_codex.py` reader, loaded by name like `meter_cursor.py.`

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-06 | Claude Opus 5.5 | Raised |
