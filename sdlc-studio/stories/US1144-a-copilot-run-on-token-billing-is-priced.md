# US1144: A Copilot run on token billing is priced per token from Copilot's dated AI-credit rates and the dollar value of a credit

> **Status:** Ready
> **Delivers:** CR0685
> **Created:** 2026-11-09
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/templates/model-prices.json, .claude/skills/sdlc-studio/scripts/lib/prices.py, .claude/skills/sdlc-studio/scripts/tests/test_prices.py
> **Epic:** EP0304
> **Points:** 3
> **Depends on:** US1143
> **Persona:** Maya Okafor

## User Story

**As a** Maya Okafor
**I want** A Copilot run on token billing is priced per token from Copilot's dated AI-credit rates and the dollar value of a credit
**So that** CR0685 is delivered by work that can be planned and checked

## Acceptance Criteria

- **AC1:** Given the shipped `templates/model-prices.json`, then it carries a Copilot token-billing block of its own, apart from the provider-API `models` entries: the US-dollar value of one AI credit, its `effective` date and a `source` on GitHub's own Copilot billing page naming the day it was read (`read YYYY-MM-DD`), and, for each model Copilot's token billing prices, its five component rates in AI credits per million tokens under the id the Copilot CLI records (the `modelMetrics` key `lib/meter_copilot.py` and `lib/harness_usage.py` read, dotted, such as `claude-sonnet-5.5` or `gpt-5.5`, not the Anthropic API's `claude-sonnet-5-5`), a component Copilot does not bill separately at the rate it bills it at, said in `note`. No id in the block is also a `models` id, so a lookup by id alone is never ambiguous. The builder reads GitHub's page; no rate is typed from memory. Fails on: rates in dollars with no credit value, an undated or unsourced block, a Copilot rate filed under a provider-API id, or an id both blocks hold.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_prices.py::CopilotTokenPriceTests::test_copilot_credit_rates_are_dated_sourced_and_keyed_by_the_copilot_id
- **AC2:** Given the captured Copilot CLI output (`tests/fixtures/harness_usage/copilot.jsonl`, model `claude-sonnet-5.5`) parsed by `harness_usage.parse`, then `prices.cost` on its components, called as `sprint lane run`'s return line calls it, returns each component's tokens times that model's credit rate per million times the credit's dollar value, summed, with `unpriced` None, the figure typed in the test from the block's rates; and `run_state.usd` over a split naming that model gives the same figure. Fails on: the reading read as not priced, priced at an Anthropic API rate, or its credit count reported as dollars.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_prices.py::CopilotTokenPriceTests::test_a_recorded_copilot_reading_is_priced_from_credits_in_dollars
- **AC3:** Given a Copilot block missing the credit's dollar value, its `effective` date or its `source`, or a model rate missing one component, then `prices.load` raises `PriceTableError` naming the block and the field, never reading the gap as zero; beside each, the shipped block loads and prices AC2's reading (the positive control). Fails on: a missing rate read as 0, or the block dropped silently.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_prices.py::CopilotTokenPriceTests::test_a_partial_copilot_block_is_refused_by_name_and_the_shipped_one_loads
- **AC4:** Given a Copilot reading naming a dotted id the Copilot block does not hold, then `prices.cost` returns `usd` None with `unpriced` naming the id, never priced at the provider-API entry of a similar name (`claude-sonnet-5-5`) or at $0; beside it, in the same test, a listed Copilot id is priced (the positive control). Fails on: dot-to-hyphen or nearest-name matching onto the API table.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_prices.py::CopilotTokenPriceTests::test_an_unlisted_copilot_id_is_not_priced_beside_a_listed_one

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-09 | sdlc-studio | Created via `new` (deterministic) |
| 2026-11-09 | Claude Opus 5.5 (run nine grooming) | Acceptance criteria and Verify lines authored at grooming |
