# US0682: review.mutation_evidence stays independent of the test-plan scope, with a fixture setting both proving the two lanes stay sequential rather than nested

> **Status:** Blocked
> **Delivers:** CR0550
> **Created:** 2026-08-21
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/transition.py, .claude/skills/sdlc-studio/scripts/tests/test_transition.py
> **Epic:** EP0217
> **Blocked by:** D0150 and CR0555. A pre-code goal review REJECTED this batch three times. The third rejection was decisive: the measurement justifying the design was taken against a throwaway script rather than the weighted pipeline `route.estimate` actually runs, and three literal readings of the criterion through the real pipeline land at 81 to 97 per cent `light` - the mirror image of the defect, in the more dangerous direction. D0150 then ruled out the class entirely: no author-declared field may gate review depth, and `Points` is author-declared. CR0555 replaces the approach - the expensive half of the gate MOVES to the terminal transition where a diff exists, rather than being banded on a signal that must be read before one does. Do not build this batch; it is kept for its review record, which cost three rounds to produce. Disposition: mutation-evidence independence - still wanted, re-target at CR0555's shape.
> **Points:** 3
> **Persona:** Maya Okafor

## User Story

**As a** Maya Okafor
**I want** review.mutation_evidence stays independent of the test-plan scope, with a fixture setting both proving the two lanes stay sequential rather than nested
**So that** CR0550 is delivered by work that can be planned and checked

## Acceptance Criteria

- [ ] **AC1** Given a project setting `review.mutation_evidence: block` AND a test-plan scope that exempts the unit, when it transitions, then the mutation-evidence lane still blocks - the two lanes ask different questions and must stay sequential, which is BG0541's defect recreated one level in
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_transition.py::MutationEvidenceIndependenceTests::test_mutation_evidence_blocks_independently_of_the_test_plan_scope
- [ ] **AC2** Given a fixture setting BOTH settings across their combinations, when each is exercised, then no combination lets one lane silently waive the other - asserted over the matrix rather than over the one pairing somebody thought to try, because a fixture setting both went green while carrying exactly this defect
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_transition.py::MutationEvidenceIndependenceTests::test_no_combination_of_the_two_settings_waives_the_other

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-21 | sdlc-studio | Created via `new` (deterministic) |
| 2026-08-21 | sdlc-studio | Groomed: acceptance criteria authored against the slice |
| 2026-08-24 | sdlc-studio | RE-GROOMED against CR0549's second and third corrections after a pre-code goal review REJECTED the first attempt: the declared basis now reads `Points` and `Affects` breadth rather than whole-file complexity, measured to move `light` from 13% to 33%. |
