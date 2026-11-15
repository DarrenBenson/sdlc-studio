# EP0306: Every cost row a run reports has a forecast and a ratio to learn from, and a row that cannot be forecast says why

> **Status:** Done
> **Derived Point Total:** 6
> **Parent:** CR0694
> **Created:** 2026-11-14
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Size:** M

## Summary

Decomposed from CR0694. Delivers the work CR0694 requested.

## Story Breakdown

- [x] [US1150: The plan records a priced, dollar and wall-clock forecast beside tokens and minutes](../stories/US1150-the-plan-records-a-priced-dollar-and-wall.md)
- [x] [US1151: The report's Estimates table shows forecast, actual and ratio for every cost row](../stories/US1151-the-report-s-estimates-table-shows-forecast-actual.md)

## Acceptance Criteria (Epic Level)

- [ ] `sprint plan --write` records a `priced_per_point` rate with its source, the measured runs it was fitted from, and the report's Priced cost and Priced per point rows show forecast, actual and ratio
- [ ] The plan records a dollar forecast, the priced forecast times the planned model's rates in `templates/model-prices.json`, naming the price table's effective date, and the Dollar cost and Dollars per point rows show a ratio
- [ ] The plan forecasts the wall-clock span from measured points per elapsed hour and the report shows its ratio; the span is still never compared with active minutes (BG0898 stands)
- [ ] A row with no measured rate reads 'not forecast: <reason>', never a bare 'not forecast', and `sprint plan` prints each row it could not forecast and why
- [ ] Forecasts stay descriptive: no command refuses or warns on a ratio, and the report says so beside the table

> Carried from the request. Author each story's own ACs against its
> slice while grooming - these are the epic's completion bar, not any
> single story's.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-14 | sdlc-studio | Created via `new` (deterministic) |
