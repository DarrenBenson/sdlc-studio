# BG1308: The product seat card's worked example names Maya Okafor as the shipped skill's Primary, which RFC0063 makes false once Abena Osei's card lands

> **Status:** Open
> **Severity:** Low
> **Points:** 1
> **Affects:** sdlc-studio/personas/seats/product.md, tools/tests/test_persona_coherence.py
> **Evidence:** sdlc-studio/personas/seats/product.md:96; D0436
> **Created:** 2026-11-09
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5; human; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-09T12:38:36Z

## Summary

Found by the product seat grooming CR0689 (2026-11-09). `sdlc-studio/personas/seats/product.md` (around lines 96-105) teaches the seat with a worked example that quotes 'the shipped skill's Primary, Maya Okafor' and her End goal 2. After US1146 makes Abena Osei the Primary (D0436), the example teaches the seat to judge against the wrong persona, and a worked example is how a seat is learned.

## Steps to Reproduce

1. After US1146 lands, read `sdlc-studio/personas/seats/product.md` around its worked example.
2. It still names Maya Okafor as the shipped skill's Primary.

## Proposed Fix

Re-point the worked example to the Primary the registry declares (Abena Osei) and one of her End goals, or word it so it names no persona by role; add a check that a seat card naming a persona as Primary agrees with the registry.

## Acceptance Criteria

- [ ] **AC1** Given this repository's persona registry, when the product seat card's worked example is read, then the persona it calls the shipped skill's Primary is the one the registry declares for the shipped skill, and the End goal it quotes is verbatim on that persona's card; or the example names no persona by role. Fails on: the example teaching the seat to judge against Maya Okafor, whom the registry lists as Secondary.
  - **Verify:** pytest tools/tests/test_persona_coherence.py::SeatCardPrimaryTests::test_the_product_seat_example_names_the_registrys_primary
- [ ] **AC2** Given a copy of the seat cards in which one calls a Secondary persona the Primary, when the check runs, then it fails naming the card and the persona, and the cards as committed pass. Fails on: a later change of Primary leaving a seat card behind with the suite green.
  - **Verify:** pytest tools/tests/test_persona_coherence.py::SeatCardPrimaryTests::test_a_seat_card_calling_another_role_primary_is_refused

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-09 | Claude Opus 5.5 | Filed |
