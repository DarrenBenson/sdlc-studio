# US1123: The sprint report states each run's and unit's estimated dollar cost and the run's per-role cost breakdown

> **Status:** Ready
> **Delivers:** CR0665
> **Created:** 2026-11-06
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint_report.py, .claude/skills/sdlc-studio/scripts/retro.py, .claude/skills/sdlc-studio/scripts/lib/run_state.py, .claude/skills/sdlc-studio/scripts/tests/test_report_usd.py, .claude/skills/sdlc-studio/reference-sprint.md, .claude/skills/sdlc-studio/templates/reports/sprint-report.html, changelog.d/US1123.md
> **Epic:** EP0299
> **Points:** 5
> **Depends on:** US1122, US1124
> **Persona:** Maya Okafor

## User Story

**As a** Maya Okafor
**I want** The sprint report states each run's and unit's estimated dollar cost and the run's per-role cost breakdown
**So that** the operator reads a run's cost in dollars and sees which role spent it

## Acceptance Criteria

- **AC1:** Given a run whose readings name models the price table prices, then the sprint report's cost section states the run's estimated US dollar cost and dollars per point beside the priced tokens, and each unit row states its own dollar figure. Fails on: dollars computed from the priced total rather than from each reading's own model and components
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_report_usd.py::ReportUsdTests::test_run_and_unit_rows_carry_dollars
- **AC2:** Given a run with a reading whose model is not priced, then the report names that model and the share of the priced tokens the dollar figure covers, and never prints $0 for it. Fails on: an unpriced reading summed in as zero dollars
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_report_usd.py::ReportUsdTests::test_an_unpriced_model_is_named_with_the_covered_share
- **AC3:** Given the retro's priced cost line, then it states dollars per point beside priced tokens per point and the price table's effective date, marked stale when `prices.stale()` says so. Fails on: a stale table's figure shown without the mark
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_report_usd.py::ReportUsdTests::test_the_retro_line_states_dollars_and_the_table_date
- **AC4:** Given a run with lane and review records, then the report's cost section carries the per-role table `sprint cost --anatomy` prints. Fails on: a report table that diverges from the command's
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_report_usd.py::ReportUsdTests::test_the_report_carries_the_per_role_table
- **AC5:** Given a reading that carries premium requests, then the report shows them as their own unit beside its tokens and dollars. Fails on: premium requests dropped or converted into tokens
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_report_usd.py::ReportUsdTests::test_premium_requests_are_their_own_unit

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-06 | sdlc-studio | Created via `new` (deterministic) |
| 2026-11-06 | Claude Opus 5.5 | Groomed: criteria and Verify checks authored for run seven (RFC0062 Phase 1) |
