# US0682: review.mutation_evidence stays independent of the test-plan scope, with a fixture setting both proving the two lanes stay sequential rather than nested

> **Status:** Draft
> **Delivers:** CR0550
> **Created:** 2026-08-21
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/transition.py, .claude/skills/sdlc-studio/scripts/tests/test_transition.py
> **Epic:** EP0217
> **Points:** 3
> **Persona:** Maya Okafor

## User Story

**As a** Maya Okafor
**I want** review.mutation_evidence stays independent of the test-plan scope, with a fixture setting both proving the two lanes stay sequential rather than nested
**So that** CR0550 is delivered by work that can be planned and checked

## Acceptance Criteria

- [ ] **AC1** Given a project setting `review.mutation_evidence: block` AND a test-plan scope that exempts the unit, when it transitions, then the mutation-evidence lane still blocks - the two lanes ask different questions and must stay sequential, which is BG0541's defect recreated one level in
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_transition.py::PlanGateScopeTests::test_mutation_evidence_blocks_independently_of_the_test_plan_scope
- [ ] **AC2** Given a fixture setting BOTH settings across their combinations, when each is exercised, then no combination lets one lane silently waive the other - asserted over the matrix rather than over the one pairing somebody thought to try, because a fixture setting both went green while carrying exactly this defect
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_transition.py::PlanGateScopeTests::test_no_combination_of_the_two_settings_waives_the_other

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-21 | sdlc-studio | Created via `new` (deterministic) |
| 2026-08-21 | sdlc-studio | Groomed: acceptance criteria authored against the slice |
| 2026-08-21 | sdlc-studio | HELD - not in the RUN batch. CR0550's correction of 2026-08-21 applies. Re-groom before planning. |
