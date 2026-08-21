# US0676: The derived half of Verification depth is delimited and a hand-edit to it is refused, while the author's judgement half survives verbatim

> **Status:** Draft
> **Delivers:** CR0548
> **Created:** 2026-08-21
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Verification depth:** functional [[derived: criteria 4; plan rows 6; executed 6; killed 6; survived 0; not-run 0; entry point 2 of 4 criteria through the shipped CLI, 2 in-process | fp 2de45defbf1c ]] (the seal is asserted by editing the field the way an author actually would - correcting a count they believe is wrong - and the escape is proved by RUNNING the named command, not by reading the sentence. Three ways past the guard are each pinned: an edit inside the delimiters, a stripped fingerprint, and a re-hash over the whole value. NOT covered: an author who edits the counts AND recomputes the seal, which is forgery rather than a hand-edit and is the same bound `_index.md` has)
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
  - **Verified:** yes (2026-08-21)
- [ ] **AC2** Given a hand-edit INSIDE the derived delimiters, when the gate runs, then it is REFUSED and the edited field is named - a derived surface nobody may hand-edit is only derived if something refuses the edit
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_gate.py::DerivedDepthLaneTests::test_a_hand_edit_inside_the_derived_half_is_refused
  - **Verified:** yes (2026-08-21)
- [ ] **AC3** Given that refusal, when it is printed, then it NAMES the command that regenerates the field, and running that command CLEARS the refusal - a refusal with no stated escape would make this batch's own depth fields uncorrectable and the tree uncommittable, which is a defect this repository has already shipped once
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_gate.py::DerivedDepthLaneTests::test_the_refusal_names_the_regenerate_command_and_it_clears_the_refusal
  - **Verified:** yes (2026-08-21)
- [ ] **AC4** Given an edit OUTSIDE the delimiters, in the judgement half, when the gate runs, then it PASSES - the paired control, because a guard that refuses every edit to the field has not distinguished the two halves it exists to distinguish
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_gate.py::DerivedDepthLaneTests::test_an_edit_to_the_judgement_half_passes
  - **Verified:** yes (2026-08-21)

## Test Plan

| Criterion | Mutant - the production change this test must fail on | Title |
| --- | --- | --- |
| AC1 | in `verify_ac.py`, replace `_DERIVED_RE.sub("", current)` with `current` in `depth_field_value`, so the whole value is rebuilt | Given a rendered `Verification depth`, when it is written, then the DERIVED half sits inside explicit delimiters and the author's judgement half - the tier, and what was deliberately not covered - sits outside them and survives regeneration verbatim, byte for byte |
| AC2 | in `verify_ac.py`, replace the `claimed == actual` comparison in `depth_edit_faults` with a bare `claimed` truth test | Given a hand-edit INSIDE the derived delimiters, when the gate runs, then it is REFUSED and the edited field is named - a derived surface nobody may hand-edit is only derived if something refuses the edit |
| AC3 | in `verify_ac.py`, delete the regenerate command from the refusal message in `depth_edit_faults` | Given that refusal, when it is printed, then it NAMES the command that regenerates the field, and running that command CLEARS the refusal - a refusal with no stated escape would make this batch's own depth fields uncorrectable and the tree uncommittable, which is a defect this repository has already shipped once |
| AC4 | in `verify_ac.py`, replace `span.group("facts")` with `match.group(2)` in `depth_edit_faults`, so the seal covers the whole field value | Given an edit OUTSIDE the delimiters, in the judgement half, when the gate runs, then it PASSES - the paired control, because a guard that refuses every edit to the field has not distinguished the two halves it exists to distinguish |
| AC4 | in `verify_ac.py`, replace the `if not span: continue` arm of `depth_edit_faults` with an appended fault | Given an edit OUTSIDE the delimiters, in the judgement half, when the gate runs, then it PASSES - the paired control, because a guard that refuses every edit to the field has not distinguished the two halves it exists to distinguish |
| AC4 | in `verify_ac.py`, skip a span carrying no fingerprint in `depth_edit_faults` | Given an edit OUTSIDE the delimiters, in the judgement half, when the gate runs, then it PASSES - the paired control, because a guard that refuses every edit to the field has not distinguished the two halves it exists to distinguish |

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-21 | sdlc-studio | Created via `new` (deterministic) |
| 2026-08-21 | sdlc-studio | Groomed: acceptance criteria authored against the slice |
| 2026-08-21 | sdlc-studio | Goal review round 2: AC2's refusal had no stated escape, which would leave this batch's own depth fields uncorrectable |
| 2026-08-21 | sdlc-studio | verify-ratchet REFUSED the stacked block my edit created: AC2 stated two claims and carried two `Verify:` lines, of which only the first would ever run. Split - the refusal is AC2, the named escape is AC3 |
