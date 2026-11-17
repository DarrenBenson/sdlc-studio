# US1286: The disclosure baseline may only shrink, and the TSD rows say the lane fails on a rise against it

> **Status:** Draft
> **Risk-class:** standard
> **Delivers:** CR0725
> **Created:** 2026-11-17
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** tools/tests/test_baselines_only_shrink.py, sdlc-studio/tsd.md, tools/tests/test_lean_tsd_refresh.py
> **Epic:** EP0363
> **Points:** 2
> **Persona:** Abena Osei

## User Story

**As a** Abena Osei
**I want** The disclosure baseline may only shrink, and the TSD rows say the lane fails on a rise against it
**So that** CR0725 is delivered by work that can be planned and checked

## Acceptance Criteria

### AC1: A commit that grows the disclosure baseline fails

- **Given** `tools/tests/test_baselines_only_shrink.py` and the committed `tools/disclosure-baseline.txt`
- **When** the baseline in the working tree holds an entry the committed version does not
- **Then** the shrink check names the file and the added entry and fails, and with an entry removed it passes. Fails on: the disclosure baseline left out of the list the check compares, so a new finding is waved through by adding a line to the file
- **Verify:** pytest tools/tests/test_baselines_only_shrink.py::BaselinesOnlyShrinkTests::test_the_disclosure_baseline_is_held_to_shrink

### AC2: The TSD rows say the lane fails on a rise against its baseline

- **Given** `sdlc-studio/tsd.md`
- **When** its Static / Lint row for Disclosure, its CI Quality Gates row for `lint:disclosure` and its NFR row for progressive disclosure are read
- **Then** both lane rows say the lane fails when a finding appears that its committed baseline does not hold and name `tools/disclosure-baseline.txt`, neither still says it exits 0 unless run with `--strict`, and the NFR row names `lint:disclosure` beside `check_budgets.py`. Fails on: the rows as they stand at grooming, which call the lane advisory and verify the requirement on line counts alone
- **Verify:** pytest tools/tests/test_lean_tsd_refresh.py::DisclosureBaselineRowTests::test_the_tsd_rows_say_the_lane_fails_on_a_rise

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-17 | sdlc-studio | Created via `new` (deterministic) |
