# BG1285: A non-UTF-8 legacy OpenCode message file is refused as 'raised UnicodeDecodeError', and a Cursor cloud reading's stamps are given the wrong unpriced reason

> **Status:** Open
> **Severity:** Low
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/scripts/lib/meter_opencode.py, .claude/skills/sdlc-studio/scripts/lib/run_state.py, .claude/skills/sdlc-studio/scripts/tests/test_meter_opencode.py, .claude/skills/sdlc-studio/scripts/tests/test_run_state.py
> **Evidence:** the between-releases review before v6.3.0 (D0427, LL0005), code leg A; repro under scratchpad rel63/legs/scratch-a/
> **Created:** 2026-11-08
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-08T13:07:39Z

## Summary

In the legacy OpenCode tree, a non-UTF-8 message file raises UnicodeDecodeError, which only `token_meters`' catch-all turns into a refusal. The reason it gives is 'raised UnicodeDecodeError', not one naming the file. Separately, a Cursor cloud reading carries no components, so its stamps are reported as 'written before the meter priced each component', which is the wrong reason.

## Steps to Reproduce

by reading.

## Proposed Fix

Catch ValueError beside OSError in messages() and refuse naming the message. Give `_priced_delta` a separate reason for a harness reading that carries no components.

## Acceptance Criteria

- [ ] **AC1** The behaviour described is corrected: In the legacy OpenCode tree, a non-UTF-8 message file raises UnicodeDecodeError, which only `token_meters`' catch-all turns into a refusal.
- [ ] **AC2** The proposed fix lands, pinned by a test: Catch ValueError beside OSError in messages() and refuse naming the message.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-08 | Claude Opus 5.5 | Filed |
