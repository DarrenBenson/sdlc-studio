# BG1331: A Grok request of 200k tokens or more is priced at xAI's short-context rate, so the meter understates the requests that cost a consuming project most

> **Status:** Open
> **Severity:** Medium
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/templates/model-prices.json, .claude/skills/sdlc-studio/scripts/lib/prices.py, .claude/skills/sdlc-studio/scripts/lib/token_meters.py, .claude/skills/sdlc-studio/scripts/tests/test_prices.py, .claude/skills/sdlc-studio/scripts/tests/test_token_meters.py
> **Evidence:** templates/model-prices.json grok-4.7 note; a consuming project's Cursor cost data, 2026-11-10
> **Created:** 2026-11-10
> **Created-by:** sdlc-studio file
> **Raised-by:** Darren Benson (operator); human; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-10T17:02:50Z

## Summary

templates/model-prices.json prices grok-4.7, grok-4.6 and grok-4.5 (and their xai/ ids) from xAI's Short context rates only. Its own note says the page's Long context rates, for a prompt of 200k tokens or more, are not used because a session total cannot tell them apart. A consuming project delivering with Grok 4.7 through Cursor found that requests over 200k tokens made up 58% of its bill (2026-11-10), so a dollar figure from this table understates its cost most where the cost is largest, and the report does not say so. BG1309 covers the same gap for Fast mode.

## Steps to Reproduce

1. Read the grok-4.7 entry in templates/model-prices.json: one input rate, no long-context rate.
2. Price a Cursor reading whose requests include prompts of 200k tokens or more.
3. Every request is priced at the short-context input rate, and the report's Dollar cost row carries no caveat.

## Proposed Fix

Record xAI's long-context rates, dated, beside the short-context ones. Where a reading carries per-request token counts, price each request of 200k tokens or more at the long-context rate. Where it holds only a total, the Dollar cost row says the figure is a lower bound for that model and why.

## Acceptance Criteria

- [ ] **AC1** The behaviour described is corrected: templates/model-prices.json prices grok-4.7, grok-4.6 and grok-4.5 (and their xai/ ids) from xAI's Short context rates only.
- [ ] **AC2** The proposed fix lands, pinned by a test: Record xAI's long-context rates, dated, beside the short-context ones.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-10 | Darren Benson (operator) | Filed |
