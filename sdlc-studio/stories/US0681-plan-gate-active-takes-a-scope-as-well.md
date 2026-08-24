# US0681: _plan_gate_active takes a SCOPE as well as a date, so the test-plan gate can be required of high-band units alone

> **Status:** Draft
> **Delivers:** CR0550
> **Created:** 2026-08-21
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/transition.py, .claude/skills/sdlc-studio/scripts/tests/test_transition.py
> **Epic:** EP0217
> **Points:** 8
> **Persona:** Maya Okafor

## User Story

**As a** Maya Okafor
**I want** _plan_gate_active takes a SCOPE as well as a date, so the test-plan gate can be required of high-band units alone
**So that** CR0550 is delivered by work that can be planned and checked

## Acceptance Criteria

- [ ] **AC1** Given a project configuration naming a SCOPE as well as a date, when the entry gate decides, then the demand for an INDEPENDENT plan-review approval applies to units at or above that band and not below it - `_test_plan_gate` does two things, and this narrows only the second
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_transition.py::PlanGateScopeTests::test_the_independent_approval_is_required_at_or_above_the_band
- [ ] **AC2** Given a unit BELOW the configured scope, when it enters implementation, then a `## Test Plan` is STILL required of it - the authoring-time rule that a criterion names a production change its test dies on is unchanged at every band, which is CR0550's own promise and the half that costs nothing
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_transition.py::PlanGateScopeTests::test_a_test_plan_is_still_required_below_the_band
- [ ] **AC3** Given the TERMINAL planned-mutant join at the other call site of `_plan_gate_active`, when a unit below the scope reaches a terminal status, then that join is not demanded of it, and a unit at or above it is refused exactly as today - the two gates are scoped together and each is asserted separately, because one function guarding two rules is how a scope silently reaches a gate nobody meant to narrow
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_transition.py::PlanGateScopeTests::test_the_terminal_join_is_scoped_at_both_ends
- [ ] **AC4** Given the gate reading a band, when it asks the estimator, then it asks for the DECLARED basis and names it - the entry gate fires before implementation, so no diff can exist there, and a gate that asked for one would refuse every unit
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_transition.py::PlanGateScopeTests::test_the_gate_asks_for_the_declared_basis
- [ ] **AC5** Given a unit whose band cannot be resolved at all, when the gate decides, then it APPLIES both halves rather than skipping them - the existing fail-towards-deeper-review rule
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_transition.py::PlanGateScopeTests::test_an_unresolvable_band_applies_the_gate

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-21 | sdlc-studio | Created via `new` (deterministic) |
| 2026-08-21 | sdlc-studio | Groomed: acceptance criteria authored against the slice |

| 2026-08-24 | sdlc-studio | RE-GROOMED against CR0549's second and third corrections after a pre-code goal review REJECTED the first attempt: the declared basis now reads `Points` and `Affects` breadth rather than whole-file complexity, measured to move `light` from 13% to 33%. |
