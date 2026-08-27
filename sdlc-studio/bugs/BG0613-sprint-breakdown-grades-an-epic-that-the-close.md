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

The question is already DECIDED. D0172 (accepted, 2026-08-27) records that a CR and an RFC are
CONTAINERS like an epic - a request is decomposed rather than delivered - and that `sprint
breakdown`, `grooming_report` and `_rung_product_blockers` all consult ONE predicate and all
skip the three container types. `TSHIRT_SIZED_TYPES` is exactly those three and
`executes_verifiers` is False for all of them, which is the evidence the decision rests on. An
earlier draft of this section re-posed the choice as open; it is not, and re-posing it
contradicts the criteria an implementer is meant to satisfy.

So `breakdown` consults `_rung_grades`, and `_rung_grades` skips the three container types
rather than epic alone. All THREE named surfaces must consult it - `_rung_product_blockers` is
a distinct call site, and a fix repairing two of the three leaves the same divergence in a
different pair.

Fixture invariant, load-bearing and easy to get wrong: `conformance.unit_is_ungroomed` already
scopes its no-criteria limb to `executes_verifiers` types, so an epic is flagged ONLY through
the placeholder or derived-only shape. An epic with no criteria at all does NOT reproduce the
divergence, and a fixture built that way makes every criterion here pass on unfixed code. The
epic must carry `refine`'s ungroomed token.

## Acceptance Criteria

- [ ] **AC1** Given a batch holding an epic that carries the ungroomed token, when `sprint breakdown` grades it, then it names the SAME set as the close's surfaces - one predicate, asked once, with no third answer
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::ContainerGradingTests::test_breakdown_and_the_close_name_the_same_set_for_an_epic
- [ ] **AC2** Given a batch holding a CR or an RFC, when it is graded, then it is SKIPPED as a container, per D0172 - a request is decomposed rather than delivered, so it carries no criteria of its own to grade
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::ContainerGradingTests::test_a_cr_and_an_rfc_are_skipped_as_containers
- [ ] **AC3** Given a batch of ordinary delivery units carrying the same ungroomed token, when it is graded, then every one is still named - the paired control, so widening the exemption to three types does not stop the grading finding real ungroomed work
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::ContainerGradingTests::test_ordinary_delivery_units_are_still_graded
- [ ] **AC4** Given `_rung_product_blockers`, the THIRD surface D0172 names, when it grades the same batch, then it agrees with the other two. A fix repairing two of three leaves the same divergence in a different pair and nothing would report it
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::ContainerGradingTests::test_the_third_surface_agrees_with_the_other_two
- [ ] **AC5** Given the shipped command, when `sprint.py breakdown` runs over a fixture batch as a subprocess, then its ungroomed list matches the close's. The Impact is operator-facing, and a breakdown consulting the right predicate in a function the CLI no longer reaches passes every library row here
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::ContainerGradingTests::test_the_breakdown_command_names_the_same_set

## Impact

`sprint plan` can refuse a batch as ungroomed and the close of that same batch can report the offending unit as not gradeable at all. Both statements come from the same repository about the same unit in the same run, and an operator reading either has no way to know the other exists. It is the defect BG0587 closed, still standing on a third surface.

## Test Plan

| Criterion | Mutant - the production change this test must fail on | Title |
| --- | --- | --- |
| AC1 | in `.claude/skills/sdlc-studio/scripts/sprint.py`, have `breakdown` consult `_rung_grades` for CR and RFC but keep its own inline test for epics, so the epic answer is computed in two places and can drift again | Given a batch holding an epic that carries the ungroomed token, when `sprint breakdown` grades it, then it names the SAME set as the close's surfaces - one predicate, asked once, with no third answer |
| AC2 | in `.claude/skills/sdlc-studio/scripts/sprint.py`, narrow `_rung_grades` back to skipping epic alone, so the exemption stops at the one type that already had it | Given a batch holding a CR or an RFC, when it is graded, then it is SKIPPED as a container, per D0172 - a request is decomposed rather than delivered, so it carries no criteria of its own to grade |
| AC3 | in `.claude/skills/sdlc-studio/scripts/sprint.py`, widen `_rung_grades` to skip any type in `TSHIRT_SIZED_TYPES` or carrying no `Points`, so an ungroomed story is exempted alongside the containers | Given a batch of ordinary delivery units carrying the same ungroomed token, when it is graded, then every one is still named - the paired control, so widening the exemption to three types does not stop the grading finding real ungroomed work |
| AC4 | in `.claude/skills/sdlc-studio/scripts/sprint.py`, replace `_rung_product_blockers`' call to the shared predicate with its own inline type test, so two surfaces consult one definition and the third keeps a copy | Given `_rung_product_blockers`, the THIRD surface D0172 names, when it grades the same batch, then it agrees with the other two. A fix repairing two of three leaves the same divergence in a different pair and nothing would report it |
| AC5 | in `.claude/skills/sdlc-studio/scripts/sprint.py`, remove the ungroomed list from `cmd_breakdown`'s output while leaving the grading correct, so the library agrees and the command reports nothing | Given the shipped command, when `sprint.py breakdown` runs over a fixture batch as a subprocess, then its ungroomed list matches the close's. The Impact is operator-facing, and a breakdown consulting the right predicate in a function the CLI no longer reaches passes every library row here |

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-25 | sdlc-studio | Filed |
