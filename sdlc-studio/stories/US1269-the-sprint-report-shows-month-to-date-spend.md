# US1269: The sprint report shows month-to-date spend against a declared monthly budget across every harness

> **Status:** Draft
> **Risk-class:** elevated
> **Delivers:** CR0716
> **Created:** 2026-11-17
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint_report.py, .claude/skills/sdlc-studio/templates/config-defaults.yaml, .claude/skills/sdlc-studio/reference-config.md, .claude/skills/sdlc-studio/scripts/tests/test_report_budget.py
> **Epic:** EP0355
> **Points:** 5
> **Persona:** Abena Osei

## User Story

**As a** Abena Osei
**I want** The sprint report shows month-to-date spend against a declared monthly budget across every harness
**So that** CR0716 is delivered by work that can be planned and checked

## Acceptance Criteria

### AC1: A project declares a monthly budget, and the default is unset

- **Given** `templates/config-defaults.yaml` and `reference-config.md`
- **When** the key `cost.monthly_budget_usd` is read from each
- **Then** the defaults file carries the key unset, the reference page documents it as a monthly budget in US dollars with a default of unset, and a value that is not a positive number is refused by name when the report reads it. Fails on: a key the reference page omits, a default that declares a budget nobody set, or a mistyped value read as no budget
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_report_budget.py::MonthlyBudgetConfigTests::test_the_key_is_documented_unset_by_default_and_a_bad_value_is_refused

### AC2: The report sets month-to-date spend beside the declared budget, across harnesses

- **Given** a project with `cost.monthly_budget_usd: 500` and three committed run records: two closed in the report's calendar month, one metered by Claude Code and one by another harness, and one closed the month before
- **When** `sprint_report.py build` writes the report for the later of the two
- **Then** the report states the month-to-date spend as the sum of the two runs' dollar costs, the budget of 500 dollars and the share of it spent, names each harness that contributed, and leaves the earlier month's run out. Fails on: one harness's spend missing from the sum, last month's run counted, or this run's cost alone presented as the month's
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_report_budget.py::MonthlyBudgetReportTests::test_month_to_date_spend_sums_every_harness_against_the_budget

### AC3: With no budget declared the report says so

- **Given** the same project with the key unset
- **When** the report is built
- **Then** it carries a line saying no monthly budget is declared and naming the key that declares one, and no percentage. Fails on: a missing row that cannot be told from a report built before the feature existed, or a share computed against zero
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_report_budget.py::MonthlyBudgetReportTests::test_an_unset_budget_is_stated_not_omitted

### AC4: Spend the price table cannot price is disclosed, not dropped

- **Given** a month in which one run's model has no price
- **When** the report is built with a budget declared
- **Then** the month-to-date figure is marked partial and names the run and the reason it could not be priced. Fails on: an unpriced run silently counted as nought, so the month reads further under budget than it is
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_report_budget.py::MonthlyBudgetReportTests::test_an_unpriced_run_marks_the_month_partial

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-17 | sdlc-studio | Created via `new` (deterministic) |
