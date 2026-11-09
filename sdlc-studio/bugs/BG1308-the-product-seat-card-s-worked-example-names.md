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

- [ ] **AC1** The behaviour described is corrected: Found by the product seat grooming CR0689 (2026-11-09).
- [ ] **AC2** The proposed fix lands, pinned by a test: Re-point the worked example to the Primary the registry declares (Abena Osei) and one of her End goals, or word it so it names no persona by role; add a check...

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-09 | Claude Opus 5.5 | Filed |
