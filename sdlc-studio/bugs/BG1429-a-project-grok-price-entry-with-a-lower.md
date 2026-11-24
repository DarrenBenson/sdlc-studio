# BG1429: A project Grok price entry with a lower long-context threshold is still booked at the shipped 200,000 threshold, so a long prompt is priced at the short rate and reads exact

> **Status:** Open
> **Severity:** Low
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/lib/meter_cursor.py, .claude/skills/sdlc-studio/scripts/tests/test_cursor_project_threshold.py, changelog.d/BG1429.md
> **Evidence:** Run twelve (RUN-01M7E52T) review of BG1393, qa-seat-BG1393-r1, verdict sdlc-studio/reviews/verdicts/BG1393/3712811b1cfd-9548042b.txt ([pre-existing])
> **Created:** 2026-11-15
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5 (run twelve orchestrator); agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-15T00:19:24Z

## Summary

`meter_cursor._rates` books a Cursor ledger against `prices.load()` with no project block (`meter_cursor._rates`, reached from `read_cli` via `read_ledger(ledger)`, which is passed no repo root), so a project `pricing.models` grok-4.7 entry whose own long-context threshold is lower than the shipped 200,000 does not move the booking: a 150,000-token prompt is priced at the project's short rate with no lower-bound label. Probe through `run_state.price_table(root)` over a project config gives $2.341 at base 35d7eaa6 and at c41f87ac.

## Steps to Reproduce

Declare a project pricing.models grok-4.7 entry with a long-context threshold of 128000 in sdlc-studio/.config.yaml, meter a Cursor ledger holding a 150,000-token prompt, and price the reading: it is priced at the short rate.

## Proposed Fix

Book the Cursor ledger against the project's price table (the same `run_state.price_table(root)` the pricing reads), so a project threshold moves the booking, or say plainly that the booking used the shipped threshold.

## Acceptance Criteria

- [ ] **AC1** Given a project `pricing.models` grok-4.7 entry with a long-context threshold of 128000 and a Cursor hook ledger holding one 150,000-token prompt, when `meter_cursor.read` meters it for that repo root, then the prompt is booked under the long-context id. Fails on: `read_cli` calls `read_ledger(ledger)`, whose `_rates()` loads the shipped table only, so the prompt is booked at the short rate and the figure reads exact.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_cursor_project_threshold.py::CursorProjectThresholdTests::test_a_project_threshold_moves_the_booking
- [ ] **AC2** Given a Cursor ledger and no project pricing block, when it is metered, then the booking is the shipped table's, unchanged. Fails on: a threading of repo_root that breaks the default table.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_cursor_project_threshold.py::CursorProjectThresholdTests::test_no_project_block_books_by_the_shipped_threshold

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-15 | Claude Opus 5.5 (run twelve orchestrator) | Filed |
| 2026-11-24 | Sam Eriksson (qa) | Groomed for run twenty-five: reproduced at HEAD, AC1 names the project threshold and the threading of repo_root through read_cli; 2 pts |
