# US0496: The gate reports its own cost per run against a budget, so a regression in gate time is as visible as a regression in behaviour

> **Status:** Done
> **Delivers:** CR0451
> **Created:** 2026-07-28
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/gate.py, .claude/skills/sdlc-studio/scripts/tests/test_gate.py
> **Epic:** EP0177
> **Points:** 3
> **Persona:** Maya Okafor

## User Story

**As a** maintainer who cannot see the gate getting slower
**I want** the gate to report its own cost against a budget each run
**So that** a regression in gate time is caught the same way a regression in behaviour is, instead of being absorbed silently

## Acceptance Criteria

### AC1: each run reports its cost against the budget

- **Given** a configured budget
- **When** the gate completes
- **Then** it prints the elapsed cost, the budget and the direction of travel against the recorded baseline
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_gate.py::GateBudgetTests::test_each_run_reports_cost_against_budget
- **Verified:** yes (2026-07-28)

### AC2: a run over budget is reported, not silently absorbed

- **Given** a run exceeding the budget
- **When** it completes
- **Then** the overage is stated plainly with the lane that dominated it, so the cause is visible rather than the total alone
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_gate.py::GateBudgetTests::test_an_over_budget_run_names_the_dominant_lane
- **Verified:** yes (2026-07-28)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-28 | sdlc-studio | Created via `new` (deterministic) |
| 2026-07-28 | Claude Fable 5 | Groomed against the operator's two policy rules |
