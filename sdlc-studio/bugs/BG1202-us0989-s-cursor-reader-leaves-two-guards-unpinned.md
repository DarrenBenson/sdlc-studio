# BG1202: US0989's Cursor reader leaves two guards unpinned and names an empty usage for a malformed answer

> **Status:** Open
> **Severity:** Low
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/scripts/lib/meter_cursor.py, .claude/skills/sdlc-studio/scripts/tests/test_meter_cursor.py, changelog.d/BG1202.md
> **Evidence:** US0989 round-1 verdict, scratchpad run5/US0989-verdict-r1.txt.
> **Created:** 2026-11-04
> **Created-by:** sdlc-studio file
> **Raised-by:** claude; human; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-04T12:39:12Z

## Summary

2026-11-04, US0989's review (qa-seat-US0989-r1, APPROVE, non-blocking). The mutant `SIGNALS = (AGENT_ENV, KEY_ENV)` passes all four tests, and under it a Claude Code session with `CURSOR_API_KEY` exported reads no tokens at all. Dropping `value >= 0` from `_count` (`meter_cursor.py`:129) passes all four tests. A 200 answer whose JSON is not an object (`[]`, `null`, a string, a number) is reported as 'it records no usage for this agent yet' (`meter_cursor.py`:140-142) rather than as a malformed answer. tokens stays None in every case.

## Steps to Reproduce

1. Apply either mutant to lib/`meter_cursor.py` and run tests/`test_meter_cursor.py`: it passes.
2. Stub the usage API to answer `[]` and read the reason.

## Proposed Fix

Assert the key alone does not signal Cursor, assert a negative count is refused, and give a non-object answer the malformed-answer reason.

## Acceptance Criteria

- [ ] **AC1** Both mutants fail a test, and a non-object answer reads as malformed.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_meter_cursor.py

## Impact

A later edit can make an exported Cursor key blank every Claude run's tokens, with the suite green.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-04 | claude | Filed |
