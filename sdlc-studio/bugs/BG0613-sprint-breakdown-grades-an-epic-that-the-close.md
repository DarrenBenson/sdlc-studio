# BG0613: sprint breakdown grades an epic that the close's two grooming surfaces both skip, so one run refuses to plan a batch and then closes saying that unit was not gradeable

> **Status:** Open
> **Severity:** Medium
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py
> **Evidence:** Adversarial review of BG0587, 2026-08-25, engineering seat. Divergence executed on a three-type fixture batch rather than read; origin dated to 5d4cc5a0 by inspection of the diff and of the base ref.
> **Created:** 2026-08-25
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

`sprint.breakdown` (sprint.py:2131) asks `conformance.unit_is_ungroomed` of EVERY type, epics included, while the close's two surfaces - `grooming_report` and `_rung_product_blockers` - now share `_rung_grades` and skip epics because an epic carries no acceptance criteria of its own. Measured on one fixture batch [EP0901, CR0901, BG0901], all ungroomed: `breakdown` names all three, the two close surfaces name BG0901 and CR0901. So `sprint plan` can REFUSE a batch for holding an ungroomed epic, and the close of that same batch can report that the epic was never gradeable. Three answers to one question, where BG0587 closed two of them. Origin established by execution: at 5d4cc5a0 `grooming_report` already carried `if not hit or hit[1] == "epic"` while `breakdown` had no filter, and `breakdown` is untouched by BG0587's diff - PRE-EXISTING, not a regression from it. Related and also unchanged: `_rung_grades` exempts only `epic`, while `TSHIRT_SIZED_TYPES` treats cr, rfc and epic alike as containers, so a CR or an RFC is still graded on criteria by both close surfaces.

## Steps to Reproduce

1. Build a fixture root holding three ungroomed units - one epic, one CR, one bug. 2. `sprint.breakdown` over that batch: it names all three as ungroomed. 3. `grooming_report` and `_rung_product_blockers` over the same batch: each names the CR and the bug, and neither names the epic. Measured 2026-08-25 on [EP0901, CR0901, BG0901].

## Proposed Fix

Ask ONE predicate. `_rung_grades` is the definition BG0587 introduced for exactly this question; `breakdown` should consult it rather than grading every type, or the exemption should be widened to the container types the sizing model already recognises (`TSHIRT_SIZED_TYPES` = cr, rfc, epic) if a CR and an RFC are also containers rather than delivery units. Decide which of the two the project means, then put it in one place - the point of the definition is that there is only one.

## Acceptance Criteria

- [ ] **AC1** Given a batch holding an epic, when `sprint breakdown` grades it, then it names the SAME set as the close's two surfaces - one predicate, asked once, where three answers stood
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::OneGroomingAnswerTests::test_breakdown_and_the_close_name_one_set
- [ ] **AC2** Given a batch holding a CR or an RFC, when it is graded, then it is SKIPPED as a container, per D0172 - a request is decomposed rather than delivered, and the model already says so twice in `TSHIRT_SIZED_TYPES` and `executes_verifiers`
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::OneGroomingAnswerTests::test_a_request_type_is_skipped_as_a_container
- [ ] **AC3** Given a batch of ordinary delivery units, when it is graded, then the answer is unchanged - the paired control, so widening the predicate does not stop the census counting what it always counted
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::OneGroomingAnswerTests::test_an_ordinary_batch_grades_unchanged

## Impact

`sprint plan` can refuse a batch as ungroomed and the close of that same batch can report the offending unit as not gradeable at all. Both statements come from the same repository about the same unit in the same run, and an operator reading either has no way to know the other exists. It is the defect BG0587 closed, still standing on a third surface.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-25 | sdlc-studio | Filed |
