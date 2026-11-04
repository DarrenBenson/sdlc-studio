# CR-0662: Measure a Cursor CLI run's tokens from the afterAgentResponse hook or a captured print-mode result, since the CLI's store keeps no usage

> **Status:** Proposed
> **Priority:** High
> **Type:** Feature
> **Affects:** .claude/skills/sdlc-studio/scripts/lib/meter_cursor.py, .claude/skills/sdlc-studio/reference-sprint.md, .claude/skills/sdlc-studio/scripts/tests/test_meter_cursor.py
> **Evidence:** US0990 builder report, 2026-11-04: the installed CLI bundle and the real stores under ~/.cursor/chats.
> **Date:** 2026-11-04
> **Created-by:** sdlc-studio file
> **Raised-by:** claude; human; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-04T13:01:26Z

## Summary

2026-11-04, US0990's build (run five). The Cursor CLI (build 2026.10.22-27dcf5f) persists no usage in its chat store: store.db holds only blobs and meta, and the conversation state's tokenDetails is context-window size, not spend. Usage appears only in the print-mode `result` line on stdout and in the `afterAgentResponse` hook payload (`input_tokens`, `output_tokens`, `cache_read_tokens`, `cache_write_tokens).` US0990 therefore reads a Cursor CLI run as not attributable. A hook that appends each response's usage to a ledger the meter reads would give the CLI a measured figure.

## Impact

Every sprint driven from the Cursor CLI reads NOT MEASURED, so its cost per point is invisible, the gap CR0611 was raised for.

## Acceptance Criteria

_None yet: add them here, or on the stories `refine` decomposes this into._

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-04 | claude | Raised |
