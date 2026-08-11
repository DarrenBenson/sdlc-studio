# BG0571: The repaired spec-agreement guards pin word patterns rather than claims, so a passage stating the OPPOSITE rule passes

> **Status:** Open
> **Created:** 2026-08-11
> **Created-by:** sdlc-studio new
> **Provenance:** dogfood
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** tools/tests/test_adr011_agreement.py, tools/tests/test_token_premise.py, tools/tests/test_trd_surface_derivation.py
> **Severity:** Medium
> **Points:** 3

## Summary

Found by the independent review of the BG0457 repair, which was APPROVED: every mutant the criteria named was killed and the diff is strictly stronger than what it replaced. This is the next layer down, and it is the same defect class one level deeper - BG0457 was `the guard compares the document to a projection of itself`; this is `the guard checks that some words co-occur`.

Three instances, each verified by executing the mutant.

`_fail_safe_sentence()` requires four terms in one sentence. Rewriting the rule in trd.md to say the opposite - a goal outside the ladder never blocks, and the escape opens when the rung could not be read - carries all four terms, so the helper returns it and the suite stays green. Dropping one term from `_FAIL_SAFE_TERMS` reddens nothing.

`_LOWER_BOUND` matches the claim as one sentence, and the NEGATED claim matches it too: `it is NOT a lower bound, because delegated and sidechain spend is supplied, not observed, yet both are fully counted` survives, in a full run and in isolation.

The stray-name check reads backticked lowercase names only, so a name in bold, or capitalised inside backticks, bypasses it.

None of these is a regression: each survived against the guards as they stood before the repair, so the repair did not introduce them and does not hold the gate. What it did was raise the guards to a level where this is now the weakest remaining rung.

## Steps to Reproduce

Each mutant applied singly, anchor asserted unique, `__pycache__` purged, `python3 -B`, restored per file. 1. Rewrite the D0062 fail-safe sentence in `sdlc-studio/trd.md` to state the opposite rule while keeping the words `absent`, `empty`, `ladder` and `block`. Run the tools suite - green. 2. Negate the lower-bound claim in either stating passage while keeping `lower bound` and `supplied`. Green. 3. Add `The **telepathy-lane** runs last.` to the TRD command-surface prose. Green.

## Proposed Fix

Assert the RULE rather than its vocabulary. For the fail-safe sentence and the lower-bound claim, the direction is the load-bearing part, so the check has to read the polarity: refuse a sentence carrying a negation of the claim it is matching, or state the claim as a canonical form the document must reproduce rather than as terms it must contain. For the stray-name check, read bold and mixed-case forms too. A guard that a paraphrase can defeat is weak; one that the opposite statement satisfies is inverted, and that is the half worth fixing first.

## Impact

The three guards over EP0168's spec-agreement work would report agreement while the specification stated the reverse of what the code does. Medium rather than High because it takes a deliberate rewrite of a specification passage to reach, no consumer path runs these guards, and the repair they sit on is a strict improvement on what shipped before it.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-11 | sdlc-studio | Created via `new` (deterministic) |
