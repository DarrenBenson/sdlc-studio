# BG1066: The product seat approves only stories that serve a Primary persona's goal, so a declared Secondary's stories have no approving lens

> **Status:** Fixed
> **Severity:** Medium
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/templates/personas/amigos/product.md, sdlc-studio/personas/seats/product.md, .claude/skills/sdlc-studio/scripts/tests/test_seat_admits_secondary.py, changelog.d/BG1066.md
> **Evidence:** RV0028 finding PER-3; templates/personas/amigos/product.md:21,:48,:78; personas/index.md:11-15; prd.md:104-106.
> **Created:** 2026-10-19
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-10-19T07:49:57Z

## Summary

The shipped product amigo (templates/personas/amigos/product.md:21, :48, :78) and this project's card (sdlc-studio/personas/seats/product.md:23, :42, :50, :80) approve 'a story [that] serves a Primary-persona goal'. A project may declare a Secondary with goals of its own: this one declares Jonah Reyes, with PRD outcomes O6-O8, eight stories and RPT0012's goal 'Jonah's team installs v6', and the goal-review brief already lists Secondary End goals (US0928). The seat's lens excludes a declared cast role.

## Steps to Reproduce

Read templates/personas/amigos/product.md:78 'Approves: a story serves a Primary-persona goal'; brief the product seat on a story whose Persona is the declared Secondary -> its charter gives it no ground to approve.

## Proposed Fix

Reword both cards: 'a Primary or Secondary persona's End goal, a Secondary never at the Primary's expense'.

## Acceptance Criteria

- [ ] **AC1** Given a story whose declared persona is a Secondary, when the shipped and the project product seat cards are read, then each approves a story that serves a Primary's or a declared Secondary's End goal, a Secondary never at the Primary's expense
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_seat_admits_secondary.py::ProductSeatLensTests::test_product_seat_admits_a_secondary_goal
  - **Verified:** yes (2026-10-19)
- [ ] **AC2** Given a cast with more than one Primary, each declaring an interface, when the seat cards are read, then each judges a unit against the Primary of the interface the unit's Affects touches, a unit touching the shipped interface is judged against its Primary, and the project card names no single Primary as the design persona
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_seat_admits_secondary.py::ProductSeatLensTests::test_product_seat_judges_against_the_interfaces_primary
  - **Verified:** yes (2026-10-19)
- [ ] **AC3** Given a single-Primary cast with no interfaces declared, when the shipped seat card is read, then its approval test reads as it does today for that Primary
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_seat_admits_secondary.py::ProductSeatLensTests::test_a_single_primary_cast_reads_as_before
  - **Verified:** yes (2026-10-19)

## Impact

Every consuming project with a Secondary persona has a product seat whose approval criterion cannot be met by that persona's work.

## Notes

- Widened on 2026-10-19 (D0380): with D0379's second Primary, the project card's 'the Primary design persona is Maya Okafor' (seats/product.md:4-5, :42, :89) would judge the maintainer's repository-only stories against Maya's goals. The same sentences carry the Secondary defect, so one unit fixes both. Delivered straight after US1079, before any of the second run's reviews.
- AC1 must fail on: either card still approving only a Primary-persona goal. AC2 must fail on: the project card naming one Primary as the design persona, or a shipped-path unit judged against the tooling Primary. AC3 must fail on: the shipped card's single-Primary reading changed for consuming projects.
- Read the cards as text through the same section the seat brief quotes, so the test checks what a reviewer is actually given.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-19 | Claude Opus 5.5 | Filed |
| 2026-10-19 | Claude Opus 5.5 | Widened to the two-Primary interface lens and groomed for the second 6.2 run (D0380); re-pointed 3 |
