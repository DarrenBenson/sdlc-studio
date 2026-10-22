# BG1122: Each meter reading now re-reads every subagent transcript from the start, so a lane, transition or report command takes about 36 s on a long session instead of 22 s

> **Status:** Open
> **Severity:** Medium
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/lib/run_state.py, .claude/skills/sdlc-studio/scripts/tests/test_run_state.py, .claude/skills/sdlc-studio/scripts/tests/test_meter_incremental_read.py, changelog.d/BG1122.md
> **Evidence:** US1091 QA review round 1, qa-seat-US1091-r1, at fcb7f071: 36 s against 22 s per reading; US1097 builder: 346 s for the first current-basis stamp.
> **Created:** 2026-10-22
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-10-22T13:54:37Z

## Summary

US1091's QA review (round 1, 2026-10-22). Since US1091 the meter reads the main transcript and every `<session>/subagents/agent-*.jsonl` once per message on every reading. On this session one reading takes about 36 s, against 22 s before; `sprint.py lane brief`, `lane return`, `transition.py set` and the report each take one, and US1097's first current-basis stamp reads the transcripts twice (about 346 s observed while suites ran). The process this epic makes cheaper in tokens gets slower in wall time with every unit.

## Steps to Reproduce

`time python3 -c` a `run_state.session_tokens` reading on a session with ~90 subagent transcripts.

## Proposed Fix

Memoise per transcript by (path, size, mtime): keep each file's per-message components and its byte offset in `.local`, and on the next reading parse only the bytes appended since. A file that shrank or changed identity is re-read whole.

## Acceptance Criteria

- [ ] **AC1** Given a reading taken, then one message appended to a transcript, when the next reading is taken, then only the appended bytes are parsed and the result equals a full re-read
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_meter_incremental_read.py::IncrementalReadTests::test_a_second_reading_parses_only_appended_bytes
- [ ] **AC2** Given a transcript that shrank or was replaced, then it is re-read whole
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_meter_incremental_read.py::IncrementalReadTests::test_a_shrunk_or_replaced_transcript_is_read_whole

## Impact

Every stamp-taking command pays a full re-read of hundreds of MB of transcript, growing with the session.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-22 | Claude Opus 5.5 | Filed |
