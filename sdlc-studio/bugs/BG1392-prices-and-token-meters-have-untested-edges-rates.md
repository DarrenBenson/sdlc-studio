# BG1392: prices and token_meters have untested edges: `_rates()` falls back to an empty table, `_list`'s long-context pop, a true threshold read as 1, and `book()` splits labelled lower bound

> **Status:** Open
> **Severity:** Low
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/scripts/lib/prices.py, .claude/skills/sdlc-studio/scripts/lib/token_meters.py, .claude/skills/sdlc-studio/scripts/tests/test_prices.py, .claude/skills/sdlc-studio/scripts/tests/test_price_edge.py, changelog.d/BG1392.md, .claude/skills/sdlc-studio/scripts/tests/test_token_meters.py
> **Evidence:** RUN-01M78TKD, 2026-11-13: lane cost builder; costfix review
> **Created:** 2026-11-13
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5 (run eleven orchestrator); agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-13T01:09:49Z

## Summary

`prices._rates()` returns an empty table when the table cannot be read, untested. `_list`'s pop of a replaced entry's long-context id (prices.py:216) has no test. `_long_context` (prices.py:195) accepts a `true` threshold as 1, and `token_meters.dollars` still labels a split from book() a lower bound with no shipped caller.

## Steps to Reproduce

Make the table unreadable; set a threshold of true.

## Proposed Fix

Reject boolean thresholds and add the three tests.

## Acceptance Criteria

- [ ] **AC1** Given an unreadable price table, a replaced long-context entry and a boolean threshold, when prices load, then each is handled as stated and pinned. Fails on: any of the three left unpinned or a boolean read as 1.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_price_edge.py::PriceEdgeTests

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-13 | Claude Opus 5.5 (run eleven orchestrator) | Filed |
