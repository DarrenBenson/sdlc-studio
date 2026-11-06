# BG1242: US1123's dollar report re-prices an unsigned page from the live price table, so `sprint sign` refuses it after a price revision, and its close wiring and end-date rule are unpinned

> **Status:** Open
> **Severity:** Medium
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint_report.py, .claude/skills/sdlc-studio/scripts/retro.py, .claude/skills/sdlc-studio/scripts/tests/test_report_usd.py, changelog.d/BG1242.md
> **Evidence:** run seven (RUN-01M6RAP7) US1123 review round 1
> **Created:** 2026-11-06
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-06T14:35:59Z

## Summary

Run seven, US1123 round 1 (REJECT; its three blocking findings are repaired in the run and not repeated here). Non-blocking: (1) The changelog and `reference-sprint.md` say the page carries the table it was priced with, "so a re-derivation prices with the same prices", but only a signed anchor is replayed: the unsigned page `sprint sign` re-derives reads the live table. Executed: after a table change `revalidate` reads invalid, `est_actual` $0.6608 becomes $1.32 and `eu_usd` $0.2432 becomes $0.4864. In this repository the table is in-tree, so sign's tree check refuses first, but in a consuming project a skill upgrade between close and sign makes sign refuse the page. (2) The close wiring is pinned by no test: replacing `run_state.stamp_cost_roles(root)` in `_file_the_report` (`sprint.py:10028`) with `pass` survives `test_report_usd`, `test_lean_close` and `test_lean_signed_report_stable` (43 passed), because every AC4 test calls `stamp_cost_roles` itself "as the close does"; the behaviour is correct by execution. (3) The retro's stale mark is judged on today rather than on the run's end as the report's is (`retro.py:1656` calls `run_state.usd` with no `today`), and the report's end-date rule is unpinned (mutant `"today": None` in `build_report` survives).

## Steps to Reproduce

1. Close a fixture run, change one model's price in `templates/model-prices.json`, then revalidate or sign the unsigned page: it reads invalid and re-derives new dollar figures. 2. In a scratch copy replace the `stamp_cost_roles` call in `_file_the_report` with `pass` and run the three modules above: all pass. 3. Set `"today": None` in `build_report`: all pass.

## Proposed Fix

Replay the filed page's own price table for an unsigned page as well as a signed one, so a re-derivation prices with the table the close used, and pin it with a price change between close and sign; or, if the live table is intended, correct the changelog and `reference-sprint.md` and have sign name the price change as its reason. Add a test that drives the close rather than `stamp_cost_roles` and asserts the role table is filed, a test for the report's end-date rule, and pass the run's end date to `run_state.usd` in `retro.py`.

## Acceptance Criteria

- [ ] **AC1** Given a closed run whose page is filed but unsigned, when one model's price in `templates/model-prices.json` changes and the page is then revalidated or put to `sprint sign`, then it reads valid and re-derives the close's `est_actual` and `eu_usd` unchanged. Fails on: `_page_readings` returning `price_table: None` for an unsigned page, so the live table is read (the executed $0.6608 to $1.32 shift).
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_report_usd.py::ReportUsdTests::test_an_unsigned_page_keeps_the_prices_it_was_filed_with
- [ ] **AC2** Given the same unsigned page with its recorded price table edited on disk after the close and its fingerprint left as filed, when it is revalidated, then it reads invalid and names the change. Fails on: replaying the table from the file with the table left out of the digest.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_report_usd.py::ReportUsdTests::test_an_edited_price_table_on_an_unsigned_page_is_named
- [ ] **AC3** Given a fixture run closed through the `sprint.py close` entry point, never by calling `stamp_cost_roles` directly, then the filed page carries the per-role table. Fails on: replacing `run_state.stamp_cost_roles(root)` in `_file_the_report` (`sprint.py`) with `pass`, which survives every current test.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_report_usd.py::ReportUsdTests::test_the_close_itself_files_the_role_table
- [ ] **AC4** Given a run that ended on a day after which the table turns stale, when the report and the retro are derived later, then both judge staleness on the run's end date and neither marks the dollars stale. Fails on: `"today": None` in `build_report`, or `retro.py` calling `run_state.usd` with no `today`.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_report_usd.py::ReportUsdTests::test_staleness_is_judged_on_the_run_s_end_date

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-06 | Claude Opus 5.5 | Filed |
| 2026-11-06 | Claude Opus 5.5 | Groomed for run eight (D0416): criteria with Verify checks, Points and Affects |
