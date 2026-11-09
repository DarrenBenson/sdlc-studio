# CR-0690: Price the xAI Grok and Cursor Composer models in model-prices.json from dated provider sources, so a run on the delivery model the operator recommends reads a dollar cost rather than not priced

> **Status:** Proposed
> **Parent:** RFC0063
> **Created:** 2026-11-09
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/templates/model-prices.json, .claude/skills/sdlc-studio/scripts/lib/prices.py, .claude/skills/sdlc-studio/scripts/tests/test_prices.py
> **Priority:** High
> **Type:** Enhancement
> **Size:** S

## Summary

RFC0063 WS5 and D7, in run nine (D0435). `templates/model-prices.json` prices Claude, OpenAI and Copilot models but holds no xAI Grok or Cursor Composer entry, so a run on the delivery model the operator recommends reads "not priced" (RFC0063, Context). Add each Grok and Composer model under the id the token meters report for it, with input, cached-input and output rates, each sourced from the provider's own published pricing and dated.

## Impact

A team running Grok or Composer through Cursor, OpenCode or another supported harness sees no money figure on its sprint report, so RFC0063 outcome O11 (cost per point in money, whichever harness ran it) fails for them. Cost metering area under D0444.

## Acceptance Criteria

- [ ] `templates/model-prices.json` prices every xAI Grok and Cursor Composer model a supported harness's meter reports, under the model id the meter reads, each entry naming its provider source URL and the date it was read.
- [ ] A run whose token readings name a Grok or a Composer model is priced in US dollars by `lib/prices.py`, and a test reads a recorded reading for each model and sees a dollar figure, not "not priced".
- [ ] A model id the table does not hold is still reported as not priced, never priced at another model's rate, and a test pins that refusal beside the positive control.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-09 | sdlc-studio | Created via `new` (deterministic) |
