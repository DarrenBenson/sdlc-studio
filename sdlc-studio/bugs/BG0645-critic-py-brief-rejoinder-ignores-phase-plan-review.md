# BG0645: critic.py brief --rejoinder ignores --phase plan-review and renders the delivery brief, so a re-review of a rejected test plan is briefed with a diff scope that does not exist

> **Status:** Open
> **Verification depth:** functional [[derived: criteria 3; plan rows 4; EVIDENCE ABSENT - the mutation ledger holds no entry for this unit, which is not the same fact as nought killed; NOT RUN 4 (AC1 row 0, AC1 row 1, AC2 row 0, AC3 row 0); entry point 0 of 3 criteria through the shipped CLI, 0 in-process; 3 undetermined (the named node could not be isolated) | fp 993019d4edcb ]]
> **Severity:** Medium
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/critic.py, .claude/skills/sdlc-studio/scripts/tests/test_critic.py
> **Created:** 2026-09-04
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

critic.py brief --unit X --seat Y --phase plan-review --rejoinder <verdict file> emits the DELIVERY re-review brief: 'You did NOT author this diff', a 'Diff scope (the unit's declared Affects - inspect with git diff/status)' block, and no test-plan section or plan-review return contract. The plan-review phase, which the same command renders correctly without --rejoinder, is dropped on the rejoinder path. A round-two plan review is therefore briefed to look for a diff before any code exists, which is the exact failure the plan-review brief's own text warns against. Hit on 2026-09-04 briefing round two of a six-unit plan review after three seats rejected in round one.

## Steps to Reproduce

1. critic.py brief --unit BG0641 --seat qa --phase plan-review > a.md (correct: test-plan section, no diff scope). 2. critic.py brief --unit BG0641 --seat qa --phase plan-review --rejoinder <a VERDICT/ISSUES/BLOCKING file> > b.md. 3. b.md carries 'Diff scope' and 'this diff' and no test plan; the phase flag had no effect.

## Proposed Fix

Route the rejoinder through the same phase switch as the first-round brief: a plan-review rejoinder quotes the prior verdict verbatim, restates the criteria and the CURRENT test plan (the artefact has been re-authored since the rejection - that is what a re-review judges), demands the probes be re-executed, and returns the plan-review contract. Pin it with a test that renders a plan-review rejoinder and asserts the absence of a diff scope and the presence of the test plan, beside the delivery-rejoinder control.

## Acceptance Criteria

- [ ] **AC1** Given a unit with a plan-review REJECT recorded, when `critic.py brief --unit <id> --seat <seat> --phase plan-review --rejoinder <verdict file>` renders, then the brief carries the plan-review charter (`There is NO diff scope`), no `Diff scope` block, the criteria as law, and the prior verdict verbatim under the RE-REVIEW section - the phase governs the shape and the rejoinder appends to it
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic.py::PlanReviewBriefTests::test_a_plan_review_rejoinder_keeps_the_plan_review_shape
- [ ] **AC2** Given a unit with a delivery REJECT recorded, when the rejoinder renders with the default phase, then it carries the `Diff scope` block as today - the control, without which a rejoinder that never renders a diff scope satisfies AC1
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic.py::PlanReviewBriefTests::test_a_delivery_rejoinder_still_carries_the_diff_scope
- [ ] **AC3** Given the plan-review phase, when `--rejoinder` and `--kind test-plan` are both given, then the brief carries the test-plan charter and the prior verdict, and a `--kind` on the delivery phase is still refused
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic.py::PlanReviewBriefTests::test_a_test_plan_rejoinder_carries_the_test_plan_charter

## Test Plan

| Criterion | Mutant - the production change this test must fail on | Title |
| --- | --- | --- |
| AC1 | in `critic.py` `brief`, resolve the phase from the rejoinder flag (`delivery` whenever a rejoinder is given) - today's code | Given a unit with a plan-review REJECT recorded, when `critic.py brief --unit <id> --seat <seat> --phase plan-review --rejoinder <verdict file>` renders, then the brief carries the plan-review charter (`There is NO diff scope`), no `Diff scope` block, the criteria as law, and the prior verdict verbatim under the RE-REVIEW section - the phase governs the shape and the rejoinder appends to it |
| AC1 | in `critic.py`, render the plan-review charter but keep the `Diff scope` block, so the shape is half plan-review | Given a unit with a plan-review REJECT recorded, when `critic.py brief --unit <id> --seat <seat> --phase plan-review --rejoinder <verdict file>` renders, then the brief carries the plan-review charter (`There is NO diff scope`), no `Diff scope` block, the criteria as law, and the prior verdict verbatim under the RE-REVIEW section - the phase governs the shape and the rejoinder appends to it |
| AC2 | in `critic.py`, drop the `Diff scope` block from every rejoinder whatever the phase | Given a unit with a delivery REJECT recorded, when the rejoinder renders with the default phase, then it carries the `Diff scope` block as today - the control, without which a rejoinder that never renders a diff scope satisfies AC1 |
| AC3 | in `critic.py`, ignore `--kind` when a rejoinder is given, so a test-plan rejoinder renders the spec charter | Given the plan-review phase, when `--rejoinder` and `--kind test-plan` are both given, then the brief carries the test-plan charter and the prior verdict, and a `--kind` on the delivery phase is still refused |

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-04 | sdlc-studio | Filed |
