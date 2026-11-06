# US1135: Price the non-Claude models the meters read, each from a dated provider source

> **Status:** Ready
> **Created:** 2026-11-06
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/templates/model-prices.json, .claude/skills/sdlc-studio/scripts/lib/prices.py, .claude/skills/sdlc-studio/scripts/sprint_report.py, .claude/skills/sdlc-studio/reference-config.md, .claude/skills/sdlc-studio/reference-sprint.md, .claude/skills/sdlc-studio/scripts/tests/test_prices.py, .claude/skills/sdlc-studio/scripts/tests/test_report_usd.py, changelog.d/US1135.md
> **Epic:** EP0300
> **Points:** 3
> **Persona:** Maya Okafor

## User Story

**As a** Maya Okafor
**I want** each non-Claude model the meters read priced from a dated provider source
**So that** a run delivered through Codex CLI, Copilot CLI or OpenCode states its dollars beside a Claude run's, and no figure rests on a guessed price

## Acceptance Criteria

- **AC1:** Given the shipped `templates/model-prices.json`, then every entry that is not a Claude model carries an `effective` date and a `source` naming the provider's own published price page (OpenAI's for the models behind Codex CLI, GitHub's for Copilot premium requests, OpenCode's for its Zen models) with the date it was read, and a model with no such source is not listed. Fails on: a non-Claude entry whose source is empty, undated or not the provider's page.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_prices.py::NonClaudePriceTests::test_every_non_claude_price_is_sourced_and_dated
- **AC2:** Given a Codex lane reading that names an OpenAI model the table lists, when the report is derived, then the unit's dollars price it at that entry, a component the provider does not bill separately carries the rate the provider bills it at (an OpenAI cache write at the input rate, said in the entry's note), and an OpenAI model with no published price reads not priced, never $0. Fails on: a Codex model priced at a Claude rate or at zero, or a cache-write price of 0 entered for a provider that bills those tokens as input.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_report_usd.py::ReportUsdTests::test_a_codex_lane_is_priced_at_its_openai_rate
- **AC3:** Given an OpenCode reading on one of OpenCode's free models, under the exact id the OpenCode reader emits (`opencode/deepseek-v4.1-flash-free` in the captured fixture), then it prices at $0 with its share counted as covered, distinct from an unlisted model, which reads not priced. Fails on: a free model left unlisted (not priced), or a paid model entered at zero.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_prices.py::NonClaudePriceTests::test_a_free_opencode_model_prices_at_zero_not_unpriced
- **AC4:** Given a run whose stamps record Copilot premium requests, then the `Premium requests` row states their dollars at the table's sourced, dated per-request price, and the token `Dollar cost` row is unchanged, premium dollars never summed into it. Fails on: premium dollars added into the token dollars (the mutant `test_premium_requests_are_their_own_unit` already names), or an absent request price read as zero.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_report_usd.py::ReportUsdTests::test_premium_requests_are_priced_on_their_own_row

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-06 | sdlc-studio | Created via `new` (deterministic) |
| 2026-11-06 | Claude Opus 5.5 | Groomed for run eight (D0416): criteria and Verify checks authored |
