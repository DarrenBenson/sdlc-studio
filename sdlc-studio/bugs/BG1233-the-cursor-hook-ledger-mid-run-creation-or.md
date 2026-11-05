# BG1233: The Cursor hook ledger: mid-run creation or deletion misreads the run, deep nesting is fatal, and the text cut is untested

> **Status:** Open
> **Severity:** Low
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/lib/meter_cursor.py, .claude/skills/sdlc-studio/scripts/cursor_usage_hook.py, .claude/skills/sdlc-studio/scripts/tests/test_meter_cursor_ledger_edges.py, changelog.d/BG1233.md, .claude/skills/sdlc-studio/scripts/tests/test_meter_cursor.py
> **Evidence:** run six reviews, scratchpad run6/*-verdict-r*.txt
> **Created:** 2026-11-05
> **Created-by:** sdlc-studio file
> **Raised-by:** claude; human; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-05T15:34:46Z

## Summary

2026-11-05, US1121's reviews. A ledger that first appears mid-run leaves the run uncovered, and one deleted mid-run reads a wrong spend (9,072 against a true 160); a deeply nested JSON line makes the hook exit 1 and the reader raise RecursionError, against the 'never fatal' and 'exits 0' docstrings; the `MAX_TEXT` cut is untested; a true/false count is written to the ledger; the repair's count guard is untested and unreachable.

## Steps to Reproduce

See the summary; each item was reproduced by its reviewer or builder.

## Proposed Fix

Read a ledger that appears or shrinks mid-run as uncovered rather than as spend, catch deep nesting as a skipped line, and pin the text cut and count types.

## Acceptance Criteria

- [ ] **AC1** A ledger created or truncated mid-run reads as not covering the run; a deeply nested line is skipped and counted, and the hook exits 0; a cut id and a boolean count are pinned.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_meter_cursor_ledger_edges.py

## Impact

A Cursor run's measured figure can be wrong in these cases.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-05 | claude | Filed |
