# US1270: The PRD, the Primary persona card and RFC0063 state the monthly budget's true status

> **Status:** Draft
> **Risk-class:** standard
> **Delivers:** CR0716
> **Created:** 2026-11-17
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** sdlc-studio/prd.md, sdlc-studio/personas/abena-osei-head-of-engineering.md, sdlc-studio/rfcs/RFC0063-human-in-the-lead-the-accountable-engineering-lead.md, tools/tests/test_prd_monthly_budget_status.py
> **Epic:** EP0355
> **Points:** 2
> **Persona:** Abena Osei

## User Story

**As a** Abena Osei
**I want** The PRD, the Primary persona card and RFC0063 state the monthly budget's true status
**So that** CR0716 is delivered by work that can be planned and checked

## Acceptance Criteria

### AC1: The PRD carries the monthly budget with the status the code supports

- **Given** `sdlc-studio/prd.md` and the shipped `templates/config-defaults.yaml`
- **When** the Feature Inventory and outcome O11 are read
- **Then** the inventory holds a row for the monthly budget, and while the defaults file carries no `cost.monthly_budget_usd` key that row is not Complete and O11 is marked Partial, naming the budget half as the part not built; once the key ships the row may read Complete and O11 drops the mark. Fails on: O11 read as served while no key declares a budget, or the mark left on after the budget view ships
- **Verify:** pytest tools/tests/test_prd_monthly_budget_status.py::MonthlyBudgetStatusTests::test_the_prd_row_and_o11_match_whether_the_budget_key_ships

### AC2: The Primary persona card and RFC0063 say the same

- **Given** `sdlc-studio/personas/abena-osei-head-of-engineering.md` and RFC0063
- **When** the card's account of the sprint report and the RFC's Decomposed-into line and fifth workstream row are read
- **Then** the card keeps the monthly budget as Abena's goal but does not describe the report as showing cost against a monthly budget while the key is absent; RFC0063's Decomposed-into names CR0716, and its fifth workstream names CR0716 as the budget view instead of a request still to be filed. Fails on: a persona card that describes a report row which does not exist, or a workstream that still reads `CR (new)` for the budget view
- **Verify:** pytest tools/tests/test_prd_monthly_budget_status.py::MonthlyBudgetStatusTests::test_the_persona_card_and_rfc0063_name_cr0716_and_claim_no_unbuilt_row

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-17 | sdlc-studio | Created via `new` (deterministic) |
