# BG1324: No test replays a page filed before the Copilot billing basis existed, a mixed run's page drops the 'plan bills by request' reason, and US1145's lane-return test copies the call instead of running it

> **Status:** Won't Fix
> **Severity:** Low
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint_report.py, .claude/skills/sdlc-studio/scripts/tests/test_report_usd.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py, changelog.d/BG1324.md
> **Evidence:** US1145-verdict-r1 (RUN-01M7061X), findings 1, 2 and 4
> **Created:** 2026-11-09
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5; human; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-09T18:08:40Z

## Summary

From US1145's QA review (qa-seat-US1145-r1, non-blocking, 2026-11-09). (1) A v6.3.0 sprint page with premium requests, filed before `pricing.copilot_billing` existed, re-derives correctly today, but a mutant at `sprint_report.py`:3867 that breaks that replay survives the suite (LC-017). (2) In a mixed run (a priced orchestrator with Copilot lanes) `_usd_reach` (`sprint_report.py`:3785) leaves out the 'plan bills by request' reason, so the page does not say why the Copilot share is priced by request. (3) The lane-return test copies the call it exercises rather than running `sprint lane return`; run through the shipped verb, the reason is right.

## Steps to Reproduce

1. Apply the `sprint_report.py`:3867 mutant from US1145-verdict-r1 and run the suite: it passes.
2. Render a page for a run with a priced orchestrator and Copilot lanes under request billing: the request-billing reason is absent.

## Proposed Fix

Add a replay test of a pre-basis page that the :3867 mutant fails; carry the billing reason through `_usd_reach` for a mixed run; run the lane-return case through the `sprint lane return` entry point.

## Acceptance Criteria

- [ ] **AC1** Given a sprint page with premium requests, filed before `pricing.copilot_billing` existed, when it is re-derived today, then its dollar and premium-request rows are the ones it was filed with. Fails on: a page with no recorded basis read as request-billed, the mutant US1145's review found alive.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_report_usd.py::ReportUsdTests::test_a_page_filed_before_the_copilot_billing_basis_re_derives_unchanged
- [ ] **AC2** Given a run with a priced orchestrator and Copilot lanes under request billing, when its page is rendered, then the dollar row's reach names the Copilot share with the 'plan bills by request' reason. Fails on: a mixed run's page not saying why part of it carries no token price.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_report_usd.py::ReportUsdTests::test_a_mixed_runs_page_says_its_copilot_share_is_billed_by_request
- [ ] **AC3** Given a Copilot lane under request billing, when its return is recorded through `sprint.py lane return`, then the recorded reason is the request-billing one. Fails on: a test that copies the call it exercises staying green while the shipped verb is wrong.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_report_usd.py::ReportUsdTests::test_a_lane_return_run_through_the_verb_records_the_request_billing_reason

## Resolution

Won't Fix under D0613: the operator approved the product seat's second proposal (D0562) because only a test or pin is missing on behaviour that is right on every path a user reaches. An unpinned replay and a missing reason line.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-09 | Claude Opus 5.5 | Filed |
| 2026-11-24 | Claude Opus 5.5 (product seat, delegate under D0545) | Won't Fix under D0613: the operator approved the product seat's second list (D0562); reason in Resolution |
