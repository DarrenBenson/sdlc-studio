# BG0571: The repaired spec-agreement guards pin word patterns rather than claims, so a passage stating the OPPOSITE rule passes

> **Status:** Fixed
> **Verification depth:** functional (each guard driven directly against both the real and the inverted statement before any test was written, and the old form confirmed to accept the inversion; the widened stray-name check found a real bold name on its first run, now declared as prose; mutation: 4 declared mutants, all KILLED, restore byte-exact)
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

## Acceptance Criteria

- [x] **AC1** Given the fail-safe rule rewritten to say the opposite - a goal outside the ladder never blocks, the escape opens - when the guard reads it, then it is NOT returned as the rule, though it carries every required term.
  - **Verify:** pytest tools/tests/test_adr011_agreement.py -k inverted_fail_safe_rule
  - **Verified:** yes (2026-08-15)
- [x] **AC2** Given a passage stating it is NOT a lower bound, when the guard reads it, then it does not count as stating the claim - the bare pattern matched it, which made the guard inverted rather than merely weak.
  - **Verify:** pytest tools/tests/test_token_premise.py -k passage_denying_the_claim
  - **Verified:** yes (2026-08-15)
- [x] **AC3** Given a name in bold or capitalised inside backticks, when the stray-name check reads the passage, then the name is seen - markup is house style, the name is the claim.
  - **Verify:** pytest tools/tests/test_trd_surface_derivation.py -k bold_and_mixed_case_names
  - **Verified:** yes (2026-08-15)
- [x] **AC4** Given an enumeration one of whose members is bold, when the run pattern reads it, then it is still recognised as an enumeration.
  - **Verify:** pytest tools/tests/test_trd_surface_derivation.py -k run_survives_a_bold_member
  - **Verified:** yes (2026-08-15)

## Impact

The three guards over EP0168's spec-agreement work would report agreement while the specification stated the reverse of what the code does. Medium rather than High because it takes a deliberate rewrite of a specification passage to reach, no consumer path runs these guards, and the repair they sit on is a strict improvement on what shipped before it.

## Resolution

All three instances assert the RULE now rather than its vocabulary.

The two claims are read WITH THEIR DIRECTION. That is the half that mattered: a guard a paraphrase can defeat is weak, but one the opposite statement satisfies is inverted, and both of these were inverted - each would have reported agreement while the specification stated the reverse of what the code does. Each test asserts the real claim is still recognised, the inversion is refused, AND that the old form really did accept the inversion, so the fixture cannot quietly stop reproducing the defect.

The stray-name check reads bold and mixed case as well as backticked lowercase. That one found something on its first run: the TRD's default-sweep passage carries **lanes** in bold, its own word for the things it enumerates, which the narrower form could never see. It is now declared as prose - which is what the guard's own refusal message asks for - so the passage could not gain or lose a member in bold without somebody deciding.

Each fix was confirmed by executing its mutant, and the guards were driven directly against both the real and the inverted statements before any test was written.

## Test Plan

| Criterion | Mutant - the production change this test must fail on | Title |
| --- | --- | --- |
| AC1 | in test_adr011_agreement.py, drop the fail-safe negation check | Given the fail-safe rule rewritten to say the opposite - a goal outside the ladder never blocks, the escape opens - when the guard reads it, then it is NOT returned as the rule, though it carries every required term. |
| AC2 | in test_token_premise.py, use the bare `_LOWER_BOUND` pattern again | Given a passage stating it is NOT a lower bound, when the guard reads it, then it does not count as stating the claim - the bare pattern matched it, which made the guard inverted rather than merely weak. |
| AC3 | in test_trd_surface_derivation.py, restore the lowercase-backticks-only name reader | Given a name in bold or capitalised inside backticks, when the stray-name check reads the passage, then the name is seen - markup is house style, the name is the claim. |
| AC4 | in test_trd_surface_derivation.py, narrow `_NAME` to backticks only | Given an enumeration one of whose members is bold, when the run pattern reads it, then it is still recognised as an enumeration. |

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-11 | sdlc-studio | Created via `new` (deterministic) |
