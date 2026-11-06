# US1122: A dated per-model price table gives every token reading an estimated cost in US dollars

> **Status:** Ready
> **Delivers:** CR0665
> **Created:** 2026-11-06
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/lib/prices.py, .claude/skills/sdlc-studio/templates/model-prices.json, .claude/skills/sdlc-studio/scripts/tests/test_prices.py, .claude/skills/sdlc-studio/reference-config.md, changelog.d/US1122.md
> **Epic:** EP0299
> **Points:** 3
> **Persona:** Maya Okafor

## User Story

**As a** Maya Okafor
**I want** A dated per-model price table gives every token reading an estimated cost in US dollars
**So that** a cheaper model or another harness shows its saving in money, not only in tokens

## Acceptance Criteria

- **AC1:** Given the shipped `templates/model-prices.json`, then every entry names a model id, its input, output, cache-read, 5-minute and 1-hour cache-write prices in US dollars per million tokens, the date they took effect and their source, and `prices.load()` refuses an entry missing any of them, naming the entry and the field. Fails on: a missing field read as a zero price
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_prices.py::PriceTableTests::test_every_entry_is_complete_and_a_partial_one_is_refused
- **AC2:** Given a reading's model and components (input, output, cache read, 5-minute and 1-hour cache write), then `prices.cost()` returns the sum of each component times its price, and a model absent from the table returns None with the model named, never 0. Fails on: an unknown model priced at zero
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_prices.py::PriceTableTests::test_cost_is_the_sum_of_components_and_an_unknown_model_is_not_priced
- **AC3:** Given a project config `pricing.models` entry, then it adds a model or replaces a shipped one, and `pricing.stale_after_days` makes `prices.stale()` name the table as stale once its newest effective date is older than that. Fails on: the override ignored, or a stale table reported fresh
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_prices.py::PriceTableTests::test_config_overrides_and_staleness

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-06 | sdlc-studio | Created via `new` (deterministic) |
| 2026-11-06 | Claude Opus 5.5 | Groomed: criteria and Verify checks authored for run seven (RFC0062 Phase 1) |
