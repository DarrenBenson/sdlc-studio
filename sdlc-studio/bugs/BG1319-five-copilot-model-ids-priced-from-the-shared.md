# BG1319: Five Copilot model ids priced from the shared OpenAI entries stay token-priced under `pricing.copilot_billing: requests`, so a request-billed Copilot run on one of them is billed twice

> **Status:** Open
> **Severity:** Low
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/lib/prices.py, .claude/skills/sdlc-studio/scripts/sprint_report.py, .claude/skills/sdlc-studio/scripts/tests/test_report_usd.py, .claude/skills/sdlc-studio/scripts/tests/test_prices.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py, changelog.d/BG1319.md
> **Evidence:** The US1145 builder's hand-back (RUN-01M7061X, 2026-11-09)
> **Created:** 2026-11-09
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5; human; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-09T17:00:54Z

## Summary

Found building US1145 (2026-11-09). gpt-6.1-sol, gpt-6.1-terra, gpt-6-astra, gpt-6-luna and gpt-5.3-codex are Copilot CLI ids that US1144 left priced from the `models` block at OpenAI's rates, because AC1 forbids an id in both blocks. US1145 makes request billing price premium requests and drop token pricing for the Copilot block, but these five are not in it, so under `copilot_billing: requests` a run on one of them is priced both per token and per premium request.

## Steps to Reproduce

1. Set `pricing.copilot_billing: requests` in a scratch project.
2. Price a Copilot reading on gpt-6-luna with premium requests recorded.
3. The run carries both a token cost and a request cost.

## Proposed Fix

Let the billing basis apply by harness rather than by price block: a Copilot reading under request billing is priced by requests alone whichever block holds its model id; pin it with a test on each of the five ids.

## Acceptance Criteria

- [ ] **AC1** Given `pricing.copilot_billing: requests` and a Copilot run on gpt-6-luna with premium requests recorded, when the sprint report prices the run, then the reading carries a request cost and no token cost, with the 'plan bills by request' reason. Fails on: the run priced both per token and per premium request.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_report_usd.py::ReportUsdTests::test_a_request_billed_copilot_run_on_a_shared_openai_id_is_priced_by_requests_alone
- [ ] **AC2** Given the same setting, when a Copilot reading is priced on each of gpt-6.1-sol, gpt-6.1-terra, gpt-6-astra, gpt-6-luna and gpt-5.3-codex, then each is unpriced by token whichever block holds its id. Fails on: the basis applied by price block, so an id outside the Copilot block stays token-priced.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_prices.py::CopilotTokenPriceTests::test_each_shared_id_is_unpriced_by_token_for_a_copilot_reading_under_request_billing
- [ ] **AC3** Given the same setting, when a Codex CLI reading on gpt-6-luna is priced, then it keeps its token price at OpenAI's rate. Fails on: the fix dropping the token price of a shared id for every harness.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_report_usd.py::ReportUsdTests::test_a_codex_reading_on_a_shared_id_keeps_its_token_price_under_request_billing

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-09 | Claude Opus 5.5 | Filed |
