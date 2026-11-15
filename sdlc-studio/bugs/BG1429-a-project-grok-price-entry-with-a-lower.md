# BG1429: A project Grok price entry with a lower long-context threshold is still booked at the shipped 200,000 threshold, so a long prompt is priced at the short rate and reads exact

> **Status:** Open
> **Severity:** Low
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/lib/meter_cursor.py, .claude/skills/sdlc-studio/scripts/lib/prices.py, .claude/skills/sdlc-studio/scripts/tests/test_cursor_project_threshold.py, changelog.d/BG1429.md, .claude/skills/sdlc-studio/scripts/tests/test_meter_cursor.py, .claude/skills/sdlc-studio/scripts/tests/test_prices.py
> **Evidence:** Run twelve (RUN-01M7E52T) review of BG1393, qa-seat-BG1393-r1, verdict sdlc-studio/reviews/verdicts/BG1393/3712811b1cfd-9548042b.txt ([pre-existing])
> **Created:** 2026-11-15
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5 (run twelve orchestrator); agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-15T00:19:24Z

## Summary

`meter_cursor._rates` books a Cursor ledger against `prices.load()` with no project block (lib/`meter_cursor.py`:249-254), so a project `pricing.models` grok-4.7 entry whose own long-context threshold is lower than the shipped 200,000 does not move the booking: a 150,000-token prompt is priced at the project's short rate with no lower-bound label. Probe through `run_state.price_table(root)` over a project config gives $2.341 at base 35d7eaa6 and at c41f87ac.

## Steps to Reproduce

Declare a project pricing.models grok-4.7 entry with a long-context threshold of 128000 in sdlc-studio/.config.yaml, meter a Cursor ledger holding a 150,000-token prompt, and price the reading: it is priced at the short rate.

## Proposed Fix

Book the Cursor ledger against the project's price table (the same `run_state.price_table(root)` the pricing reads), so a project threshold moves the booking, or say plainly that the booking used the shipped threshold.

## Acceptance Criteria

- [ ] **AC1** Given a project grok-4.7 entry with a long-context threshold of 128000, when a Cursor ledger holding a 150,000-token prompt is metered and priced, then the prompt is booked and priced at the long-context rate, or the figure names that the shipped threshold was used. Fails on: the short rate with the figure reading exact.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_cursor_project_threshold.py::CursorProjectThresholdTests

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-15 | Claude Opus 5.5 (run twelve orchestrator) | Filed |
