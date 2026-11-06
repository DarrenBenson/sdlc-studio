# CR-0685: Price a GitHub Copilot run per token in AI credits, the billing Copilot moved to on 2026-06-01, and keep the premium-request price only for plans still billed by request

> **Status:** Proposed
> **Priority:** Medium
> **Type:** Improvement
> **Size:** M
> **Affects:** .claude/skills/sdlc-studio/templates/model-prices.json, .claude/skills/sdlc-studio/scripts/lib/prices.py, .claude/skills/sdlc-studio/reference-config.md, .claude/skills/sdlc-studio/scripts/tests/test_prices.py
> **Evidence:** the orchestrator's friction log (R8-F8), from run eight (RUN-01M6RZQZ) US1135's build
> **Date:** 2026-11-06
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-06T20:38:20Z

## Summary

US1135 ships a US$0.04 premium-request price for Copilot (`pricing.premium_request`, `templates/model-prices.json`). Its builder found that Copilot moved to token billing in AI credits on 2026-06-01, so that price now applies only to Pro and Pro+ annual plans still on request billing, and the price table holds no Copilot per-token rate.

## Impact

Every Copilot run on token billing is priced at a rate its plan no longer pays, on the report and the lane return line alike, so the cross-harness cost comparison EP0299 exists for reads Copilot on the wrong basis.

## Acceptance Criteria

- [ ] `templates/model-prices.json` carries Copilot's per-token rates in AI credits, the US-dollar value of a credit and the date they were read, for each model Copilot's token billing prices
- [ ] A Copilot reading is priced per token from those rates by default, and the premium-request price applies only when the project's config names request billing
- [ ] `reference-config.md` states which Copilot plans each basis covers and the date Copilot changed basis, and a test prices one Copilot reading under each basis to different dollar figures

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-06 | Claude Opus 5.5 | Raised |
