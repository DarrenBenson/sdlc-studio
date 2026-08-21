# US0676: The derived half of Verification depth is delimited and a hand-edit to it is refused, while the author's judgement half survives verbatim

> **Status:** Draft
> **Delivers:** CR0548
> **Created:** 2026-08-21
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/verify_ac.py, .claude/skills/sdlc-studio/scripts/gate.py, .claude/skills/sdlc-studio/scripts/tests/test_verify_ac.py, .claude/skills/sdlc-studio/scripts/tests/test_gate.py
> **Depends on:** US0675 - the guard refuses a hand-edit to the DERIVED half, which has no meaning until the derivation exists. D0149 requires this lane to land last, in the gate-lane commit.
> **Epic:** EP0217
> **Points:** 3
> **Persona:** Maya Okafor

## User Story

**As a** Maya Okafor
**I want** The derived half of Verification depth is delimited and a hand-edit to it is refused, while the author's judgement half survives verbatim
**So that** CR0548 is delivered by work that can be planned and checked

## Acceptance Criteria

- [ ] **AC1** Given a rendered `Verification depth`, when it is written, then the DERIVED half sits inside explicit delimiters and the author's judgement half - the tier, and what was deliberately not covered - sits outside them and survives regeneration verbatim, byte for byte
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_verify_ac.py::DerivedDepthTests::test_the_judgement_half_survives_regeneration_verbatim
- [ ] **AC2** Given a hand-edit INSIDE the derived delimiters, when the gate runs, then it is REFUSED and the edited field is named - a derived surface nobody may hand-edit is only derived if something refuses the edit
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_gate.py::DerivedDepthLaneTests::test_a_hand_edit_inside_the_derived_half_is_refused
- [ ] **AC3** Given that refusal, when it is printed, then it NAMES the command that regenerates the field, and running that command CLEARS the refusal - a refusal with no stated escape would make this batch's own depth fields uncorrectable and the tree uncommittable, which is a defect this repository has already shipped once
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_gate.py::DerivedDepthLaneTests::test_the_refusal_names_the_regenerate_command_and_it_clears_the_refusal
- [ ] **AC4** Given an edit OUTSIDE the delimiters, in the judgement half, when the gate runs, then it PASSES - the paired control, because a guard that refuses every edit to the field has not distinguished the two halves it exists to distinguish
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_gate.py::DerivedDepthLaneTests::test_an_edit_to_the_judgement_half_passes

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-21 | sdlc-studio | Created via `new` (deterministic) |
| 2026-08-21 | sdlc-studio | Groomed: acceptance criteria authored against the slice |
| 2026-08-21 | sdlc-studio | Goal review round 2: AC2's refusal had no stated escape, which would leave this batch's own depth fields uncorrectable |
| 2026-08-21 | sdlc-studio | verify-ratchet REFUSED the stacked block my edit created: AC2 stated two claims and carried two `Verify:` lines, of which only the first would ever run. Split - the refusal is AC2, the named escape is AC3 |
