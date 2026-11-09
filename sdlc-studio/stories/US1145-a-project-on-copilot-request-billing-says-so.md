# US1145: A project on Copilot request billing says so in its config, and only then are its premium requests priced in dollars

> **Status:** Ready
> **Delivers:** CR0685
> **Created:** 2026-11-09
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/lib/prices.py, .claude/skills/sdlc-studio/scripts/sprint_report.py, .claude/skills/sdlc-studio/reference-config.md, .claude/skills/sdlc-studio/scripts/tests/test_prices.py, .claude/skills/sdlc-studio/scripts/tests/test_report_usd.py
> **Epic:** EP0304
> **Points:** 2
> **Persona:** Maya Okafor

## User Story

**As a** Maya Okafor
**I want** A project on Copilot request billing says so in its config, and only then are its premium requests priced in dollars
**So that** CR0685 is delivered by work that can be planned and checked

## Acceptance Criteria

- **AC1:** Given a project config with no `pricing.copilot_billing`, then a Copilot run's sprint report prices its Copilot-block models' tokens from the credit rates in the Dollar cost row, and states its premium requests on their own row, counted but not priced, the row's basis naming token billing and the key that switches it. Fails on: the premium requests priced at the `premium_request` price under token billing, or summed into the Dollar cost row.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_report_usd.py::ReportUsdTests::test_token_billing_prices_copilot_tokens_and_counts_premium_requests_unpriced
- **AC2:** Given `pricing.copilot_billing: requests`, then the report prices the premium requests at the table's `premium_request` price, with its date, on their own row, and the Copilot-block models' tokens read not priced with the reason that the plan bills by request, never $0 and never at the credit rates; `prices.cost` on such a reading, as the lane return line calls it, gives the same reason. Fails on: both bases priced at once (the run billed twice), or the tokens read as free.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_report_usd.py::ReportUsdTests::test_request_billing_prices_premium_requests_and_leaves_copilot_tokens_unpriced
- **AC3:** Given one Copilot run carrying tokens and premium requests, priced once under each basis, then the two reports state different dollar figures, each the one the test types: the tokens times the credit rates under `tokens`, the premium requests times the request price under `requests`. Fails on: the basis ignored, so both reports state the same figure.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_report_usd.py::ReportUsdTests::test_one_copilot_run_prices_differently_under_each_basis
- **AC4:** Given `pricing.copilot_billing` set to anything other than `tokens` or `requests`, then `prices.load` raises `PriceTableError` naming the key and the two values it takes; beside it, each of the two values loads (the positive control). Fails on: an unknown value read as either basis.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_prices.py::CopilotTokenPriceTests::test_copilot_billing_takes_tokens_or_requests_and_refuses_anything_else
- **AC5:** Given `reference-config.md#pricing`, then its key table states `pricing.copilot_billing` with its default `tokens`, says `requests` is for a Copilot Pro or Pro+ annual plan kept on request-based billing and `tokens` for every other plan, and names 1 June 2026 as the day GitHub moved Copilot to token billing in AI credits. Fails on: the key undocumented, or the plans or the date missing.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_prices.py::CopilotTokenPriceTests::test_the_configuration_reference_states_the_copilot_billing_basis

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-09 | sdlc-studio | Created via `new` (deterministic) |
| 2026-11-09 | Claude Opus 5.5 (run nine grooming) | Acceptance criteria and Verify lines authored at grooming |
