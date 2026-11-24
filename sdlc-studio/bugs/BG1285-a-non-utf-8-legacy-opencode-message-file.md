# BG1285: A non-UTF-8 legacy OpenCode message file is refused as 'raised UnicodeDecodeError', and a Cursor cloud reading's stamps are given the wrong unpriced reason

> **Status:** Won't Fix
> **Severity:** Low
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/scripts/lib/meter_opencode.py, .claude/skills/sdlc-studio/scripts/lib/run_state.py, .claude/skills/sdlc-studio/scripts/tests/test_meter_opencode.py, .claude/skills/sdlc-studio/scripts/tests/test_run_state.py, changelog.d/BG1285.md
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

- [ ] **AC1** Given a legacy OpenCode storage tree in which one message file of this repository's session is not UTF-8, when the OpenCode meter reads it, then the reading is tokens None with a reason naming that message file, and the same tree with the file re-saved as UTF-8 reads its tokens. Fails on: the refusal reaching the page as 'raised UnicodeDecodeError' from the catch-all, naming no file.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_meter_opencode.py::OpenCodeReaderTests::test_a_non_utf8_legacy_message_is_refused_by_name
- [ ] **AC2** Given a run whose stamps come from a harness reading that carries no components (a Cursor cloud reading), when the run total is formed, then `priced` is None and `priced_reason` says the harness's reading carries no components, while a stamp written before the meter priced each component keeps the reason it has. Fails on: a current harness reading reported as a stamp 'written before the meter priced each component'.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_run_state.py::RunTokenStampTests::test_a_reading_without_components_is_not_called_a_legacy_stamp

## Resolution

Won't Fix under D0613: the operator approved the product seat's second proposal (D0562) because the change it asks for is a wording preference, not a defect a user meets. Refusal reason text for a non-UTF-8 legacy file.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-08 | Claude Opus 5.5 | Filed |
| 2026-11-24 | Claude Opus 5.5 (product seat, delegate under D0545) | Won't Fix under D0613: the operator approved the product seat's second list (D0562); reason in Resolution |
