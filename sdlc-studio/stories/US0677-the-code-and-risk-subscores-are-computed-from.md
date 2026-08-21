# US0677: The code and risk subscores are computed from the hunks a unit CHANGES against the base ref, not from every function in every declared file

> **Status:** Draft
> **Delivers:** CR0549
> **Created:** 2026-08-21
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/route.py, .claude/skills/sdlc-studio/scripts/complexity.py, .claude/skills/sdlc-studio/scripts/tests/test_route.py
> **Epic:** EP0217
> **Points:** 5
> **Persona:** Maya Okafor

## User Story

**As a** Maya Okafor
**I want** The code and risk subscores are computed from the hunks a unit CHANGES against the base ref, not from every function in every declared file
**So that** CR0549 is delivered by work that can be planned and checked

## Acceptance Criteria

- [ ] **AC1** Given a unit and a base ref, when `route.estimate` computes `code` and `risk`, then both are derived from the HUNKS the unit changes against that ref, not from every function in every file its `Affects` names
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_route.py::DiffScopedEstimateTests::test_the_code_and_risk_subscores_read_the_changed_hunks
- [ ] **AC2** Given a two-line change to a large module and a rewrite of that same module, when both are scored, then they produce DIFFERENT bands. The discrimination is the whole point: today both inherit the module's worst function and score identically, which is why 87% of this repository's 603 bugs tier `full`
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_route.py::DiffScopedEstimateTests::test_a_small_change_and_a_rewrite_of_one_file_band_differently
- [ ] **AC3** Given a change that is small in line count but lands inside a high-complexity branch, when it is scored, then the surrounding function's complexity still contributes - a diff-scoped estimate that reads added lines in isolation would band a one-line change to load-bearing code as trivial, which is the failure mode this must not introduce
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_route.py::DiffScopedEstimateTests::test_a_small_change_in_a_complex_branch_is_not_banded_trivial

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-21 | sdlc-studio | Created via `new` (deterministic) |
| 2026-08-21 | sdlc-studio | Groomed: acceptance criteria authored against the slice |
