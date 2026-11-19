# BG1266: The dollar report and price table leave the run's end date, a signed table edit, the premium-request override and four price slots unpinned, and word an unsigned table edit as a tree change

> **Status:** Open
> **Severity:** Low
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint_report.py, .claude/skills/sdlc-studio/scripts/retro.py, .claude/skills/sdlc-studio/scripts/lib/prices.py, .claude/skills/sdlc-studio/scripts/lib/meter_opencode.py, .claude/skills/sdlc-studio/reference-config.md, .claude/skills/sdlc-studio/scripts/tests/test_report_usd.py, .claude/skills/sdlc-studio/scripts/tests/test_prices.py, .claude/skills/sdlc-studio/scripts/tests/test_meter_opencode.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py, .claude/skills/sdlc-studio/scripts/tests/test_retro.py, changelog.d/BG1266.md
> **Evidence:** run eight (RUN-01M6RZQZ) BG1242 review round 1 and US1135 review round 1 ([new] and [pre-existing]), and the orchestrator's friction log (R8-F6)
> **Created:** 2026-11-06
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-06T20:38:12Z

## Summary

From BG1242's review: (1) AC4's Verify test cannot tell the run's end date from the day it is read, because the fixture's run ends now (`.claude/skills/sdlc-studio/scripts/tests/test_report_usd.py:441`): mutants `"today": date.today()` (`sprint_report.py:4534`), `_run_end` returning `date.today()` and `_run_end` reading `started_at` (`retro.py:1641`) all pass the module, and a run ended two days after a table effective long enough ago to be stale today kills all three. (2) A signed page's on-disk table edit is named `envelope.price_table` (`sprint_report.py:5669`) and no test pins it: dropping the envelope entry from `held` and `filed` passes and only weakens the name to 'fingerprint'. (3) On an unsigned marked page, doubling the haiku input price on disk reads INVALID through `sprint_report.py check`, naming `est_actual[6]` and `eu_usd[0]` with 'the tree re-derives' (`sprint_report.py:5680`) although the tree did not move: the remedy is right, the wording is not. From US1135's review: (4) the `pricing.premium_request` override (`reference-config.md:344`) is pinned by no test: `if False:` on `lib/prices.py:235` survives `test_prices.py` and `test_report_usd.py`; (5) the refusal of a negative premium-request price is unpinned: dropping `or usd < 0` (`lib/prices.py:175`) survives; (6) `gpt-5.3-codex`'s `cache_write_1h` slot (`templates/model-prices.json:22`) is unpinned, the AC2 usage carrying no 1-hour write; (7) the `gpt-6-astra`, `gpt-6.1-terra` and `gpt-6-luna` rates are checked by no test: `gpt-6-astra` input 10.0 to 1.0 (`model-prices.json:18`) survives both modules. Pre-existing, from the same review: (8) the OpenCode session meter names no model (`lib/meter_opencode.py:160`), so only a lane-run reading launched with `-m opencode/<model>` can price the free model, and a session-metered OpenCode run reads not priced.

## Steps to Reproduce

Apply each mutant named above and run `test_report_usd.py` and `test_prices.py`: each survives. For (3), on an unsigned marked page double the haiku input price in its table on disk and run `sprint_report.py check`: INVALID, worded 'the tree re-derives'. For (8), meter an OpenCode session run: the reading carries no model and no dollar figure.

## Proposed Fix

Add the end-date probe (a run ended two days after an old table), a signed-page table-edit test asserting `envelope.price_table`, and one test per US1135 mutant (the override through `prices.load`, a negative request price refused, a nonzero 1-hour write for `gpt-5.3-codex`, a typed rate for each of the three untested models); on an unsigned page, name a moved figure whose inputs re-derive unchanged as a price-table edit; have the OpenCode session meter read the model where the store records it, and say in `reference-config.md` when it cannot.

## Acceptance Criteria

- [ ] **AC1** Given a run that ended two days after a table's effective date, read on a day when that table is stale, when the report builds its dollar row, then staleness is judged at the run's end date. Fails on: today's date or the run's `started_at` used in its place.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_report_usd.py::ReportUsdTests::test_staleness_is_judged_at_the_runs_end_not_today
- [ ] **AC2** Given a signed page and an unsigned marked page whose price table is edited on disk with the tree unmoved, when `sprint_report.py check` runs on each, then the signed page names `envelope.price_table` and the unsigned page names the moved figures as a price-table edit. Fails on: the signed page naming only a fingerprint, or the unsigned page saying the tree re-derives.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_report_usd.py::ReportUsdTests::test_a_table_edit_is_named_as_one_signed_or_unsigned
- [ ] **AC3** Given a `pricing.premium_request` override, a negative one, a `gpt-5.3-codex` usage with a nonzero 1-hour write, and a usage on each of `gpt-6-astra`, `gpt-6.1-terra` and `gpt-6-luna`, when `prices.load` and `cost()` run, then the override applies, the negative price is refused, and each figure matches the table's typed rate. Fails on: any of the four mutants the summary names passing the module.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_prices.py::NonClaudePriceTests::test_the_request_override_and_every_shipped_rate_are_pinned
- [ ] **AC4** Given an OpenCode store that records the session's model, when the session meter reads it, then the reading names the model and is priced; given a store that records none, the reading says it is not priced and `reference-config.md` says when that happens. Fails on: a session-metered OpenCode run reading not priced although the store names its model.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_meter_opencode.py::OpenCodeReaderTests::test_a_session_reading_names_the_model_the_store_records

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-06 | Claude Opus 5.5 | Filed |
