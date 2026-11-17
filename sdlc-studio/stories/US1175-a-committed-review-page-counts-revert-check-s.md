# US1175: A committed review page counts revert-check's verdict per unit over at least five signed runs, with re-totalled sums

> **Status:** Draft
> **Risk-class:** standard
> **Delivers:** CR0630
> **Created:** 2026-11-17
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** sdlc-studio/reviews/revert-check-yield.md, tools/tests/test_revert_check_yield_page.py
> **Epic:** EP0316
> **Points:** 3
> **Persona:** Abena Osei

## User Story

**As a** Abena Osei
**I want** A committed review page counts revert-check's verdict per unit over at least five signed runs, with re-totalled sums
**So that** CR0630 is delivered by work that can be planned and checked

## Acceptance Criteria

### AC1: Each counted run matches its run record

- **Given** the committed page `sdlc-studio/reviews/revert-check-yield.md` and the run records under `sdlc-studio/reports/runs/`
- **When** the page's table of runs is read
- **Then** it lists at least five signed runs, each with the `base_ref` and `verified_sha` its run record holds and the seconds its pass took. Fails on: fewer than five runs, a ref that differs from the run record, or a run with no seconds
- **Verify:** pytest tools/tests/test_revert_check_yield_page.py::RevertCheckYieldPageTests::test_each_counted_run_matches_its_run_record

### AC2: Every unit of a counted run has a verdict row

- **Given** the page's per-unit table and each counted run's batch
- **When** the two are compared
- **Then** every unit of each batch has one row whose verdict is passed, refused or not judged, a refused row names the criteria and a not judged row names its cause, as `verify_ac.py revert-check` printed them. Fails on: a unit left off the page, a verdict outside the three, or a not judged row with no cause
- **Verify:** pytest tools/tests/test_revert_check_yield_page.py::RevertCheckYieldPageTests::test_every_unit_of_a_counted_run_has_a_verdict_row

### AC3: The stated totals equal the rows re-totalled

- **Given** the page's stated totals of refused, passed and not judged units and of seconds
- **When** the per-unit and per-run rows are re-totalled
- **Then** each stated total equals its re-total. Fails on: a total that is off by one from its rows, or a totals line with a figure the rows cannot produce
- **Verify:** pytest tools/tests/test_revert_check_yield_page.py::RevertCheckYieldPageTests::test_the_stated_totals_equal_the_rows_re_totalled

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-17 | sdlc-studio | Created via `new` (deterministic) |
