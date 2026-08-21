# US0681: _plan_gate_active takes a SCOPE as well as a date, so the test-plan gate can be required of high-band units alone

> **Status:** Draft
> **Delivers:** CR0550
> **Created:** 2026-08-21
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/transition.py, .claude/skills/sdlc-studio/scripts/tests/test_transition.py
> **Epic:** EP0217
> **Points:** 5
> **Persona:** Maya Okafor

## User Story

**As a** Maya Okafor
**I want** _plan_gate_active takes a SCOPE as well as a date, so the test-plan gate can be required of high-band units alone
**So that** CR0550 is delivered by work that can be planned and checked

## Acceptance Criteria

- [ ] **AC1** Given a project configuration naming a SCOPE as well as a date, when `_plan_gate_active` decides, then it applies the test-plan gate to units at or above that band only, rather than to every unit created after the date
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_transition.py::PlanGateScopeTests::test_the_gate_applies_to_the_configured_band_only
- [ ] **AC2** Given a unit BELOW the configured scope, when it transitions to a terminal status, then it is not held for a planned-mutant join; and given a unit at or above it, then it is refused exactly as today. Both legs, because a scope that exempts everything and a scope that exempts nothing both pass a one-sided test
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_transition.py::PlanGateScopeTests::test_below_scope_passes_and_at_scope_is_refused
- [ ] **AC3** Given a unit whose band cannot be resolved, when the gate decides, then it APPLIES the gate rather than skipping it - matching the existing fail-towards-deeper-review rule, so an unscoreable unit cannot buy an exemption by being unscoreable
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_transition.py::PlanGateScopeTests::test_an_unresolvable_band_applies_the_gate

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-21 | sdlc-studio | Created via `new` (deterministic) |
| 2026-08-21 | sdlc-studio | Groomed: acceptance criteria authored against the slice |
| 2026-08-21 | sdlc-studio | HELD - not in the RUN batch. CR0550's correction of 2026-08-21 applies: this narrows the mutant join at the transition boundary only. `review.test_plan_after` is read in `transition.py` alone; the pre-code plan review fires from `plan_review.triggers` and is untouched by this story. Re-groom before planning. |
