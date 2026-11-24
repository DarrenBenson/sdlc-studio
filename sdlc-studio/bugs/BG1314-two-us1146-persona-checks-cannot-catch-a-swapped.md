# BG1314: Two US1146 persona checks cannot catch a swapped Primary, and `validate.py personas` compares the whole Interface cell, so a card reverted to Primary passes AC2's own Verify

> **Status:** Won't Fix
> **Severity:** Low
> **Points:** 2
> **Affects:** tools/tests/test_persona_coherence.py, tools/tests/test_lean_prd_refresh.py, sdlc-studio/personas/jonah-reyes-team-lead.md, .claude/skills/sdlc-studio/scripts/validate.py, .claude/skills/sdlc-studio/scripts/tests/test_validate.py, changelog.d/BG1314.md
> **Evidence:** US1146-verdict-r1 (RUN-01M7061X) and its mutant log
> **Created:** 2026-11-09
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5; human; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-09T14:31:03Z

## Summary

From US1146's QA review (qa-seat-US1146-r1, non-blocking, 2026-11-09). (1) tools/tests/`test_persona_coherence.py`:749 accepts Trevor Hale's Boundaries naming Rowan Achterberg as the shipped skill's Primary and Abena Osei as the tooling Primary, and :458 accepts Jonah Reyes's cast line calling Abena the tooling Primary: the suite stays green under either swap, the class US1079's round-1 review found. (2) Pre-existing: validate.py:1283-1293 compares the whole Interface cell, so US1146 AC2's Verify passes with Maya Okafor's card reverted to Primary; only AC3's Verify catches it. (3) Found building US1147: jonah-reyes-team-lead.md:69 still says Trevor Hale wants 'central governance held by a bureaucracy', which US1147 narrowed away; US1146 kept Jonah's card fixed outside its cast lines, so it is left for this fix. (4) From US1148's review (qa-seat-US1148-r1): nothing pins O5's own wording, only its two citations, so a reworded O5 passes. (5) o10_trace_problems requires exactly one `goal serves: O10 -` line, but no test feeds it two, so loosening it to 'at least one' passes.

## Steps to Reproduce

1. In a scratch copy, swap the two Primaries' interfaces in Trevor Hale's Boundaries and run tools/tests/`test_persona_coherence.py`: it passes.
2. Revert Maya Okafor's card to Primary for the shipped skill and run US1146 AC2's Verify: it passes.

## Proposed Fix

Pin each Primary to its own interface by name in both checks, and have validate.py compare the cast role per interface rather than the cell as a whole; add the swap and the revert as failing fixtures.

## Acceptance Criteria

- [ ] **AC1** Given scratch copies of the cards in which the two Primaries' interfaces are swapped in Trevor Hale's Boundaries, and in Jonah Reyes's cast line, when the persona coherence checks read each copy, then each swap is reported, and the cards as committed pass. Fails on: a check that accepts either Primary beside either interface.
  - **Verify:** pytest tools/tests/test_persona_coherence.py::TwoPrimaryCastTests::test_a_primary_swapped_to_the_other_interface_fails_trevors_boundaries_and_jonahs_cast_line
- [ ] **AC2** Given two Primary cards whose Interface cells name the same interface in different words, when `validate.py personas` runs, then it reports the second Primary for that interface and exits 1; two Primaries on different interfaces still pass. Fails on: comparing the cell as a whole, so a card reverted to Primary passes.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_validate.py::PersonaWellFormedTests::test_two_primaries_naming_one_interface_in_different_words_are_reported
- [ ] **AC3** Given Jonah Reyes's card and Trevor Hale's card, when Jonah's Negative persona line is read, then it describes Trevor's wants as Trevor's own card now does, with no 'central governance held by a bureaucracy'. Fails on: Jonah's card describing a negative persona Trevor's card no longer describes.
  - **Verify:** pytest tools/tests/test_persona_coherence.py::ServedAndNegativeTests::test_jonahs_negative_persona_line_agrees_with_trevors_card
- [ ] **AC4** Given a PRD copy whose O5 is reworded with its two citations kept, and a `sprint.py plan --serves O10` output carrying two `goal serves: O10 -` lines, when the outcome checks read each, then each is reported. Fails on: O5 pinned by its citations alone, or `o10_trace_problems` loosened to 'at least one' line.
  - **Verify:** pytest tools/tests/test_lean_prd_refresh.py::OutcomeCitationTests::test_a_reworded_o5_and_a_second_o10_line_are_each_reported

## Resolution

Won't Fix under D0613: the operator approved the product seat's second proposal (D0562) because only a test or pin is missing on behaviour that is right on every path a user reaches. Persona coherence tests that cannot catch a swap.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-09 | Claude Opus 5.5 | Filed |
| 2026-11-24 | Claude Opus 5.5 (product seat, delegate under D0545) | Won't Fix under D0613: the operator approved the product seat's second list (D0562); reason in Resolution |
