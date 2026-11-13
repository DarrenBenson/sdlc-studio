# BG1391: The report's Dollar cost row does not carry the lower-bound label for a Grok figure priced from a session total, so a lower bound reads as exact

> **Status:** Open
> **Severity:** Medium
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint_report.py, .claude/skills/sdlc-studio/scripts/lib/run_state.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py, .claude/skills/sdlc-studio/scripts/tests/test_grok_lower_bound_row.py, changelog.d/BG1391.md, .claude/skills/sdlc-studio/scripts/tests/test_run_state.py
> **Evidence:** RUN-01M78TKD, 2026-11-13: lane cost builder; costfix and round-2 reviews, BG1331
> **Created:** 2026-11-13
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5 (run eleven orchestrator); agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-13T01:09:23Z

## Summary

The label from the Grok long-context fix exists only on `prices.Cost.lower_bound` and `token_meters.dollars.` `_run_usd` (`sprint_report.py`:3849) merges delegated agents' Grok session totals into a Cursor split that lists the long-context id, and the run-level sum of sessions does likewise, so the Dollar cost row (`run_state.usd`, `sprint_report)` shows the figure with no label.

## Steps to Reproduce

Price a run holding a delegated Grok session of 200k tokens or more and read the Dollar cost row.

## Proposed Fix

Carry `lower_bound` through the delegated merge and the run-level sum.

## Acceptance Criteria

- [ ] **AC1** Given a Grok session total merged into a booked split, when the report's Dollar cost row prints, then it carries the lower-bound label. Fails on: the row showing the figure unlabelled.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_grok_lower_bound_row.py::GrokLowerBoundRowTests

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-13 | Claude Opus 5.5 (run eleven orchestrator) | Filed |
