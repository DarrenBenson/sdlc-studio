# BG1321: Trevor Hale's Scenario check misses a capitalised offer and a negation outside its word list, so changelog.d/US1147.md claims more than the AC7 test holds

> **Status:** Won't Fix
> **Severity:** Low
> **Points:** 1
> **Affects:** tools/tests/test_persona_coherence.py, changelog.d/BG1321.md
> **Evidence:** BG1318-verdict-r1 (RUN-01M7061X), findings 1 and 3
> **Created:** 2026-11-09
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5; human; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-09T17:32:16Z

## Summary

From BG1318's QA review (qa-seat-BG1318-r1, non-blocking findings 1 and 3, 2026-11-09; both present before BG1318). (1) The outside check at tools/tests/`test_persona_coherence.py`:988 is case-sensitive, so a Scenario reading 'Sync to an enterprise tracker is offered.' passes, and changelog.d/US1147.md:15-17 says any offer is caught. (3) NEGATION (:212) is still a word list, so 'used to decline', 'seldom declines' and 'Nobody declines' pass. The verdict carries a scratch-tried fix for each.

## Steps to Reproduce

1. In a scratch copy, append 'Sync to an enterprise tracker is offered.' to Trevor Hale's Scenario and run the AC7 test: it passes.
2. Replace 'declines' with 'seldom declines' in the declining sentence and run it again: it passes.

## Proposed Fix

Match the wants case-insensitively in the outside check, and require the declining verb to stand with no qualifier rather than listing negations; reword the US1147 fragment to the claim the test then holds. Pin both with the verdict's mutants.

## Acceptance Criteria

- [ ] **AC1** Given a copy of Trevor Hale's Scenario with 'Sync to an enterprise tracker is offered.' appended, when the AC7 check reads it, then the check fails naming the want outside the clause that declines it. Fails on: a case-sensitive match passing a capitalised offer.
  - **Verify:** pytest tools/tests/test_persona_coherence.py::ServedAndNegativeTests::test_a_capitalised_offer_outside_the_declining_clause_fails_the_scenario_check
- [ ] **AC2** Given copies of the Scenario whose declining sentence reads 'seldom declines', 'used to decline' and 'Nobody declines', when the AC7 check reads each, then each fails, and the card as committed passes. Fails on: a list of negations that misses a qualifier outside it.
  - **Verify:** pytest tools/tests/test_persona_coherence.py::ServedAndNegativeTests::test_a_qualified_declining_verb_fails_the_scenario_check

## Further evidence

- 2026-11-12 (RUN-01M77177, qa-seat-US1147-r1 round 3): AC7's verifier still passes a capitalised 'Sync' sentence and negations its word list misses ('Nobody declines', 'seldom declines'). Reported against this bug at review, not blocking US1147.

## Resolution

Won't Fix under D0564: the operator approved the product seat's proposal (D0562) because only a test or pin is missing on behaviour that is right on every path a user reaches. Scenario check misses a capitalised offer; the persona text is correct and only a test and its changelog claim over-reach. The qa re-check at 81e02369 found the defect still present (D0563), so this closes it as not worth its cost, not as fixed.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-09 | Claude Opus 5.5 | Filed |
| 2026-11-21 | Claude Opus 5.5 (product seat, delegate under D0545) | Won't Fix under D0564: the operator approved the product seat's list (D0562); reason in Resolution |
