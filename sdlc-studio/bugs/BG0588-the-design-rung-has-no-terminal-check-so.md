# BG0588: the design rung has no terminal check, so a unit left at Draft or Blocked closes it clean

> **Status:** Fixed
> **Severity:** High
> **Verification depth:** functional [[derived: criteria 2; plan rows 2; executed 2; killed 2; survived 0; not-run 0; entry point 0 of 2 criteria through the shipped CLI, 2 in-process | fp ae72f7a3576b ]] (two criteria over the close pre-flight: a groomed unit short of the rung's terminal blocks, and one at the terminal does not. Both mutants executed and killed against the current tree)
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py
> **Created:** 2026-08-17
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

BG0582 replaced the delivery-status question with a grooming question for the design rung. Grooming is the rung's product, but it is not the rung's whole bar: nothing now asks what STATUS the unit reached. A unit that is groomed and left at `Draft`, or at `Blocked`, returns zero blockers where the base ref returned one. The rung's stated terminal is Ready, and no lane checks it. Separately, `unit_is_ungroomed` asks its `no-criteria` question only for types where `executes_verifiers` holds, so a design batch carrying a CR, RFC, epic or spike with zero acceptance criteria passes the rung's own bar entirely - an epic loses a blocker the base ref raised.

## Steps to Reproduce

Found by a round-3 adversarial review of BG0582, 2026-08-17, by driving the close pre-flight over ten fixture shapes at seven rung spellings against both refs. A design-rung batch whose single story is groomed and carries `Status: Draft` returns 0 blockers at HEAD and 1 at base ref 7697ee36; the same is true for `Blocked`. A design-rung batch whose only unit is an epic with no `## Acceptance Criteria` section returns 0 blockers at HEAD and 1 at base. Both have run-window delivery evidence, so BG0586 - which is about units groomed OUTSIDE the window - does not cover either.

## Proposed Fix

Fold this into BG0586's redesign of the design rung's bar rather than patching it separately: that unit is already about replacing a state check with a real one, and this is the same question asked of status instead of criteria. The bar wants to be, per unit, groomed AND at the rung's declared terminal AND produced within the run. For the type half, decide whether a design batch may legitimately contain a type `unit_is_ungroomed` cannot judge - if it may, the rung needs a different question for those types; if it may not, `sprint plan` should refuse them into a design batch rather than the close discovering it.

## Acceptance Criteria

- [ ] **AC1** Given a `design` rung unit that is groomed but sits at Draft, when the close pre-flight runs, then it reports a blocking row naming the unit and the rung's terminal - groomed is not finished, and a rung that did half its work closed clean
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::RungTerminalAndProductTests::test_a_groomed_unit_short_of_the_terminal_blocks
- [ ] **AC2** Given a `design` rung unit that is groomed AND at the rung's terminal, when the pre-flight runs, then it reports no blocker - the paired control, because a check that blocks a rung which did exactly what it exists to do is one nobody keeps
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::RungTerminalAndProductTests::test_a_groomed_unit_at_the_terminal_does_not_block

## Test Plan

| Criterion | Mutant - the production change this test must fail on | Title |
| --- | --- | --- |
| AC1 | in `sprint.py`, `continue` in `_rung_product_blockers` as soon as a unit is groomed | Given a `design` rung unit that is groomed but sits at Draft, when the close pre-flight runs, then it reports a blocking row naming the unit and the rung's terminal - groomed is not finished, and a rung that did half its work closed clean |
| AC2 | in `sprint.py`, drop the terminal comparison from `_rung_product_blockers`, so every groomed unit blocks | Given a `design` rung unit that is groomed AND at the rung's terminal, when the pre-flight runs, then it reports no blocker - the paired control, because a check that blocks a rung which did exactly what it exists to do is one nobody keeps |

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-17 | sdlc-studio | Filed |
