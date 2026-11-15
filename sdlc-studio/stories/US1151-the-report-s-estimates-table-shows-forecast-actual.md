# US1151: The report's Estimates table shows forecast, actual and ratio for every cost row

> **Status:** Ready
> **Delivers:** CR0694
> **Created:** 2026-11-14
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint_report.py, .claude/skills/sdlc-studio/scripts/tests/test_lean_report.py, .claude/skills/sdlc-studio/scripts/tests/test_lean_report_minutes_like_for_like.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py, .claude/skills/sdlc-studio/scripts/tests/test_report_usd.py, .claude/skills/sdlc-studio/scripts/tests/test_lane_priced.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_estimates_cost_rows.py, changelog.d/US1151.md, .claude/skills/sdlc-studio/help/sprint.md, .claude/skills/sdlc-studio/reference-sprint.md, .claude/skills/sdlc-studio/reference-evidence-schema.md, tools/check_budgets.py
> **Epic:** EP0306
> **Points:** 3
> **Depends on:** US1150
> **Persona:** Abena Osei

## User Story

**As a** head of engineering whose teams take changes through a change board
**I want** the report's Estimates table shows forecast, actual and ratio for every cost row
**So that** I know what each team's delivery costs per point and can hold it to a monthly budget

## Acceptance Criteria

- **AC1:** Given a run whose snapshot holds a priced forecast, when `sprint_report.py show` renders its page, then the Priced cost and Priced per point rows show forecast, actual and an actual-over-forecast ratio.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_estimates_cost_rows.py::PricedRowsTests::test_priced_rows_show_forecast_actual_ratio
- **AC2:** Given a snapshot with a dollar forecast, when the page renders, then Dollar cost and Dollars per point show a ratio, and the basis names the price table's effective date.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_estimates_cost_rows.py::DollarRowsTests::test_dollar_rows_show_ratio_and_price_date
- **AC3:** Given a wall-clock forecast, when the page renders, then the Wall-clock span row shows its forecast and ratio, and the Minutes row is still never compared with the span.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_estimates_cost_rows.py::SpanRowTests::test_span_row_has_ratio_and_minutes_row_unchanged
- **AC4:** Given a run with no rate for a row, when the page renders, then that row reads 'not forecast: <reason>' (never bare), the page states beside the table that forecasts are descriptive, and a page filed before this change re-derives with its old rows unchanged.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_estimates_cost_rows.py::UnforecastRowTests::test_reason_text_descriptive_note_and_old_page_replay

## Notes

- Serves Abena Osei's End goal 3; delivers part of CR0694 (D0476).
- AC1 must fail on: `est_forecast` still the literal 'not forecast'; a ratio computed from the tokens row; ratio inverted (forecast over actual).
- AC2 must fail on: Dollar rows keeping 'no ratio'; the ratio taken against the Priced row rather than the dollar forecast; the effective date dropped from the basis.
- AC3 must fail on: The span ratio computed against active minutes; the Minutes row's forecast replaced by the span forecast.
- AC4 must fail on: A bare 'not forecast'; the descriptive note absent; an old filed page's fingerprint or rows moving on re-derivation.
- Rows are built in `scripts/sprint_report.py`: `_priced_row` :3761, `_priced_point_row` :3795, `_usd_rows` :3885 (inner row() hard-codes 'not forecast' and 'no ratio' for Dollar cost, Dollars per point), the Wall-clock span row at :4093 `(est_forecast` 'not forecast', `est_ratio` 'no ratio'), `_estimate_row` :3684 builds the ratio, `_estimates_section` :4033. Per-unit forecast comes from the ledger at :3650 (reads plan.get(...)).
- A filed page must replay as filed: new behaviour needs a rule mark in the envelope, following the `*_RULE` constants near :4554-4601 (e.g. `PRICED_UNIT_RULE`, `USD_RULE`) and the 'page filed before keeps its columns' branch at ~:5466. Without it the existing signed RPT pages re-derive differently.
- Reads the snapshot keys written by the first story `(forecast_priced`, `forecast_usd`, `forecast_span_minutes`, rates). Use `plan_totals-style` summing: a figure any live row lacks is None, never a partial sum.
- Descriptive note: put the sentence in the Estimates section basis, not a refusal. Existing tests asserting 'not forecast' or 'no ratio' on these rows `(test_sprint.py`, `test_lean_report.py` etc.) will need updating; grep each Measure name.
- Consuming-facing text: British English, no em dashes, no ids.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-14 | sdlc-studio | Created via `new` (deterministic) |
| 2026-11-14 | Claude Opus 5.5 (run twelve grooming, D0476) | Groomed: criteria with Verify lines, must-fail notes, Affects with the tests each change exercises and this unit's fragment |
| 2026-11-15 | Claude Opus 5.5 (run twelve) | Affects gains the evidence annex and its line ceiling: the annex's conformance test, landed earlier this run, requires the new `cost_forecast` envelope mark to be documented |
