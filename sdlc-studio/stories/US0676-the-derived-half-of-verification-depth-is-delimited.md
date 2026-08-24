# US0676: The derived half of Verification depth is delimited and a hand-edit to it is refused, while the author's judgement half survives verbatim

> **Status:** Draft
> **Closed with findings in:** BG0606 - the test-plan plan review REJECTed this unit's plan, and the plan-review gate was overridden at the close on the operator's recorded decision to carry it rather than repair it in this run. The rows are named in BG0606 and the tests that would bind them already exist.
> **Delivers:** CR0548
> **Created:** 2026-08-21
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Verification depth:** functional [[derived: criteria 9; plan rows 9; executed 9; killed 9; survived 0; not-run 0; entry point 4 of 9 criteria through the shipped CLI, 5 in-process | fp ab7d90c4e1be ]] (the seal is asserted by editing the field the way an author actually would - correcting a count they believe is wrong - and the escape is proved by RUNNING the named command, not by reading the sentence. Three ways past the guard are each pinned: an edit inside the delimiters, a stripped fingerprint, and a re-hash over the whole value. NOT covered: an author who edits the counts AND recomputes the seal, which is forgery rather than a hand-edit and is the same bound `_index.md` has)
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
- [ ] **AC5** Given a `Verification depth` carrying NO derived half at all, when the gate runs, then it is left alone - most of this corpus is hand-authored, and a guard that refused 600 artefacts on the commit that shipped it is one that gets switched off rather than satisfied
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_gate.py::DerivedDepthLaneTests::test_a_field_with_no_derived_half_is_left_alone
  - **Verified:** yes (2026-08-24)
- [ ] **AC6** Given a derived span whose fingerprint has been DELETED rather than edited, when the gate runs, then it is still REFUSED - otherwise removing the seal is a free bypass for the author who edited the counts
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_gate.py::DerivedDepthLaneTests::test_a_span_stripped_of_its_seal_is_still_refused
  - **Verified:** yes (2026-08-24)
- [ ] **AC7** Given a SECOND derived span appended to a field that already carries a sealed one, when the gate runs, then it is REFUSED wherever the second span sits - a field carries exactly one derived half, so a second is a hand-edit by construction, and judging only the first made the verdict depend on position
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_gate.py::DerivedDepthLaneTests::test_a_second_derived_span_appended_to_the_field_is_refused
  - **Verified:** yes (2026-08-24)
- [ ] **AC8** Given a `Verification depth` that WRAPS onto a second line, when a regeneration is attempted, then it is REFUSED rather than rewritten - the line-anchored match would rewrite line one and strand the rest, which is the one live shape in which AC1's byte-for-byte guarantee is false, and five tracked units carry it
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_verify_ac.py::DerivedDepthTests::test_a_field_wrapping_onto_a_second_line_is_refused
  - **Verified:** yes (2026-08-24)
- [ ] **AC9** Given a `Verification depth` carrying no tier at all, when a regeneration is attempted, then it is REFUSED rather than written - splicing a derived span into an empty value leaves `[[derived:` parsing as the tier, which is the judgement half AC1 exists to protect
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_verify_ac.py::DerivedDepthTests::test_a_tier_less_field_is_refused_rather_than_written
  - **Verified:** yes (2026-08-24)

## Test Plan

| Criterion | Mutant - the production change this test must fail on | Title |
| --- | --- | --- |
| AC1 | in `verify_ac.py`, replace `_DERIVED_RE.sub("", current)` with `current` in `depth_field_value`, so the whole value is rebuilt | Given a rendered `Verification depth`, when it is written, then the DERIVED half sits inside explicit delimiters and the author's judgement half - the tier, and what was deliberately not covered - sits outside them and survives regeneration verbatim, byte for byte |
| AC2 | in `verify_ac.py`, replace the `claimed == actual` comparison in `depth_edit_faults` with a bare `claimed` truth test | Given a hand-edit INSIDE the derived delimiters, when the gate runs, then it is REFUSED and the edited field is named - a derived surface nobody may hand-edit is only derived if something refuses the edit |
| AC3 | in `verify_ac.py`, delete the regenerate command from the refusal message in `depth_edit_faults` | Given that refusal, when it is printed, then it NAMES the command that regenerates the field, and running that command CLEARS the refusal - a refusal with no stated escape would make this batch's own depth fields uncorrectable and the tree uncommittable, which is a defect this repository has already shipped once |
| AC4 | in `verify_ac.py`, replace `span.group("facts")` with `match.group(2)` in `depth_edit_faults`, so the seal covers the whole field value | Given an edit OUTSIDE the delimiters, in the judgement half, when the gate runs, then it PASSES - the paired control, because a guard that refuses every edit to the field has not distinguished the two halves it exists to distinguish |
| AC5 | in `verify_ac.py`, replace the `if not spans: continue` arm of `depth_edit_faults` with an appended fault | Given a `Verification depth` carrying NO derived half at all, when the gate runs, then it is left alone - most of this corpus is hand-authored, and a guard that refused 600 artefacts on the commit that shipped it is one that gets switched off rather than satisfied |
| AC6 | in `verify_ac.py`, skip a span carrying no fingerprint in `depth_edit_faults` | Given a derived span whose fingerprint has been DELETED rather than edited, when the gate runs, then it is still REFUSED - otherwise removing the seal is a free bypass for the author who edited the counts |
| AC7 | in `verify_ac.py`, replace the `finditer` span iteration in `depth_edit_faults` with `_DERIVED_SPAN_RE.search(...)`, so only the first span is judged | Given a SECOND derived span appended to a field that already carries a sealed one, when the gate runs, then it is REFUSED wherever the second span sits - a field carries exactly one derived half, so a second is a hand-edit by construction, and judging only the first made the verdict depend on position |
| AC8 | in `verify_ac.py`, delete the wrapped-field guard from `write_depth`, so a field carrying a continuation line is rewritten on line one alone | Given a `Verification depth` that WRAPS onto a second line, when a regeneration is attempted, then it is REFUSED rather than rewritten - the line-anchored match would rewrite line one and strand the rest, which is the one live shape in which AC1's byte-for-byte guarantee is false, and five tracked units carry it |
| AC9 | in `verify_ac.py`, replace the empty-tier condition in `write_depth` with `False`, so a field with no tier is spliced anyway | Given a `Verification depth` carrying no tier at all, when a regeneration is attempted, then it is REFUSED rather than written - splicing a derived span into an empty value leaves `[[derived:` parsing as the tier, which is the judgement half AC1 exists to protect |

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-21 | sdlc-studio | Created via `new` (deterministic) |
| 2026-08-21 | sdlc-studio | Groomed: acceptance criteria authored against the slice |
| 2026-08-21 | sdlc-studio | Goal review round 2: AC2's refusal had no stated escape, which would leave this batch's own depth fields uncorrectable |
| 2026-08-21 | sdlc-studio | verify-ratchet REFUSED the stacked block my edit created: AC2 stated two claims and carried two `Verify:` lines, of which only the first would ever run. Split - the refusal is AC2, the named escape is AC3 |
