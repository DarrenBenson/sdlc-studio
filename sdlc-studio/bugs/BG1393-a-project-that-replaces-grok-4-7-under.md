# BG1393: A project that replaces grok-4.7 under pricing.models loses grok-4.7@long-context from its own table, so run_state.usd prices only part of the reading

> **Status:** Open
> **Severity:** Medium
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/lib/prices.py, .claude/skills/sdlc-studio/scripts/lib/run_state.py, .claude/skills/sdlc-studio/scripts/tests/test_prices.py, .claude/skills/sdlc-studio/scripts/tests/test_replaced_grok_long_context.py, changelog.d/BG1393.md, .claude/skills/sdlc-studio/scripts/tests/test_run_state.py
> **Evidence:** RUN-01M78TKD, 2026-11-13: BG1305 review
> **Created:** 2026-11-13
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5 (run eleven orchestrator); agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-13T01:10:19Z

## Summary

`_list` in prices.py (BG1331) pops the long-context id of a replaced entry, while the Cursor ledger still books long responses by the shipped table. `run_state.usd` therefore prices only part of the reading and lists the long-context id as not priced.

## Steps to Reproduce

Replace grok-4.7 in pricing.models and price a ledger with a long response.

## Proposed Fix

Keep the long-context rate paired with its base.

## Acceptance Criteria

- [ ] **AC1** Given a project pricing.models entry replacing grok-4.7, when a Cursor ledger holds long-context responses, then `run_state.usd` prices the whole reading or says plainly it cannot. Fails on: a part priced and the long-context id listed as unpriced.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_replaced_grok_long_context.py::ReplacedGrokLongContextTests

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-13 | Claude Opus 5.5 (run eleven orchestrator) | Filed |
