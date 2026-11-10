# CR-0694: The plan forecasts every cost row the report measures, so each run's cost has a ratio to learn from

> **Status:** Proposed
> **Parent:** RFC0063
> **Priority:** High
> **Type:** enhancement
> **Size:** M
> **Date:** 2026-11-10
> **Created-by:** sdlc-studio file
> **Raised-by:** Darren Benson (operator); human; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-10T12:22:13Z

## Summary

RPT0028's Estimates table forecasts only Points, Minutes and Tokens. Priced cost, Priced per point, Dollar cost, Dollars per point and Wall-clock span read 'not forecast'. The plan snapshot (`lib/run_state.py` `PLAN_SNAPSHOT` and `forecast_row`) records two rates only, `tokens_per_point` and `minutes_per_point`, and `sprint_report.py` writes 'not forecast' for the rest. Dollars per point is the operator's first concern, and a figure never forecast gives no ratio to learn from.

Evidence: runs seven, eight and nine measured 1.18M, 1.09M and 0.90M priced tokens per point. A forecast from them would have said about 1.06M for run nine, against 0.90M measured (about 0.85x); that ratio is on no page.

## Impact

Serves O11 and Abena Osei's End goal 3 (RFC0063 WS5, cost you can predict). Every plan and report changes; no gate is added and nothing refuses on a ratio.

## Acceptance Criteria

- [ ] `sprint plan --write` records a `priced_per_point` rate with its source, the measured runs it was fitted from, and the report's Priced cost and Priced per point rows show forecast, actual and ratio
- [ ] The plan records a dollar forecast, the priced forecast times the planned model's rates in `templates/model-prices.json`, naming the price table's effective date, and the Dollar cost and Dollars per point rows show a ratio
- [ ] The plan forecasts the wall-clock span from measured points per elapsed hour and the report shows its ratio; the span is still never compared with active minutes (BG0898 stands)
- [ ] A row with no measured rate reads 'not forecast: <reason>', never a bare 'not forecast', and `sprint plan` prints each row it could not forecast and why
- [ ] Forecasts stay descriptive: no command refuses or warns on a ratio, and the report says so beside the table

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-10 | Darren Benson (operator) | Raised |
