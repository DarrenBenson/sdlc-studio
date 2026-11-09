# US1143: A run on an xAI Grok or Cursor Composer model reads a dollar cost from dated provider prices, not "not priced"

> **Status:** Ready
> **Delivers:** CR0690
> **Created:** 2026-11-09
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/templates/model-prices.json, .claude/skills/sdlc-studio/scripts/tests/test_prices.py, .claude/skills/sdlc-studio/reference-config.md
> **Epic:** EP0303
> **Points:** 2
> **Persona:** Maya Okafor

## User Story

**As a** Maya Okafor
**I want** A run on an xAI Grok or Cursor Composer model reads a dollar cost from dated provider prices, not "not priced"
**So that** CR0690 is delivered by work that can be planned and checked

## Acceptance Criteria

- **AC1:** Given the shipped `templates/model-prices.json`, then it prices each xAI Grok and each Cursor Composer model a supported harness's reading names, under the id that reading carries: the `--model` slug `sprint lane run --harness cursor` passes to `cursor-agent` and records as the reading's model (Cursor CLI prints none, so `harness_usage.parse` takes the caller's), and OpenCode's `<provider>/<model>` id (such as `xai/<model>`). Each entry carries input, `cache_read` (cached input) and output rates and both cache-write slots, a component the provider does not bill separately at the rate it bills it at, said in `note`; and each entry's `source` is the provider's own published pricing page (xAI's for Grok, Cursor's for Composer) naming the day it was read (`read YYYY-MM-DD`), no earlier than its `effective` date. The builder reads those pages; no rate is typed from memory or an aggregator. Fails on: no Grok or no Composer entry, an entry whose source is another provider's page or a reseller's, an undated read, or an id no harness's reading carries.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_prices.py::NonClaudePriceTests::test_every_grok_and_composer_price_names_its_provider_page_and_the_day_read
- **AC2:** Given, for each Grok and Composer entry, a captured reading of the harness that names it (`tests/fixtures/harness_usage/cursor.json` parsed by `harness_usage.parse` with the Cursor slug as `model`, `opencode.jsonl` with the OpenCode id), then `prices.cost` on that reading's components returns a US dollar figure equal to each component's tokens times the entry's rate per million, summed, with `unpriced` None, the expected figure typed in the test from the entry's rates. Fails on: the reading read as not priced, priced at another model's rate, or at $0.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_prices.py::NonClaudePriceTests::test_a_recorded_grok_and_composer_reading_is_priced_in_dollars
- **AC3:** Given a Grok id and a Composer id the table does not hold, each a listed id with a suffix (as `opencode/deepseek-v4.1-flash` stands beside the listed `-free` entry), then `prices.cost` returns `usd` None with `unpriced` naming the id, and `run_state.usd` lists it under `unpriced` with its share, never summed in at the listed sibling's rate or at $0; beside it, in the same test, the listed sibling is priced (the positive control). Fails on: prefix or nearest-name matching, or an unlisted id read as free.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_prices.py::NonClaudePriceTests::test_an_unlisted_grok_or_composer_id_is_not_priced_beside_a_listed_one
- **AC4:** Given `reference-config.md#pricing` and the table's `about` text, then each names xAI's and Cursor's own pricing pages among those a non-Claude model is listed from, and the id form each harness's reading carries for them (the Cursor `--model` slug, the OpenCode `<provider>/<model>` id). Fails on: either still naming only OpenAI and OpenCode as the non-Claude sources.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_prices.py::NonClaudePriceTests::test_the_configuration_reference_names_the_grok_and_composer_sources

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-09 | sdlc-studio | Created via `new` (deterministic) |
| 2026-11-09 | Claude Opus 5.5 (run nine grooming) | Acceptance criteria and Verify lines authored at grooming |
