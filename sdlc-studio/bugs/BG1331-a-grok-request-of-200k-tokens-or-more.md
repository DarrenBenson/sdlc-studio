# BG1331: A Grok request of 200k tokens or more is priced at xAI's short-context rate, so the meter understates the requests that cost a consuming project most

> **Status:** Open
> **Severity:** Medium
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/templates/model-prices.json, .claude/skills/sdlc-studio/scripts/lib/prices.py, .claude/skills/sdlc-studio/scripts/lib/token_meters.py, .claude/skills/sdlc-studio/scripts/tests/test_prices.py, .claude/skills/sdlc-studio/scripts/tests/test_token_meters.py, changelog.d/BG1331.md
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

- [ ] **AC1** templates/model-prices.json records xAI's Long context rates beside the Short context ones for grok-4.7, grok-4.6, grok-4.5 and their xai/ ids, dated and sourced: input 4.00, cached input 1.00 (0.60 for grok-4.5) and output 12.00 US dollars per million tokens, for a request whose prompt is 200k tokens or more, billed at that rate for all its tokens (docs.x.ai/developers/pricing, Text API, read 2026-11-12). Fails on: a long-context rate missing, or differing from those figures.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_prices.py::GrokLongContextRatesTests
- [ ] **AC2** Where a reading carries each request's prompt size, a Grok request of 200k prompt tokens or more is priced at the long-context rate for all its tokens and one under 200k at the short rate; where a reading carries only a session total, its Grok dollar figure is labelled a lower bound rather than presented as exact. Fails on: a request of 200k or more priced at the short rate, or a session-total Grok figure shown without the lower-bound label.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_token_meters.py::GrokLongContextPricingTests

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-10 | Darren Benson (operator) | Filed |
| 2026-11-12 | Claude Opus 5.5 (run eleven orchestrator) | Groomed for run eleven (D0469, D0470): criteria rewritten with runnable Verify lines on the at-HEAD triage's evidence |
