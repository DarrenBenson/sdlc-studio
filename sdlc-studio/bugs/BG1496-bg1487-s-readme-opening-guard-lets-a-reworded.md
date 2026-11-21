# BG1496: BG1487's README-opening guard lets a reworded approval claim through, though its docstring says it never would

> **Status:** Won't Fix
> **Severity:** Low
> **Points:** 1
> **Affects:** tools/tests/test_readme_front_door.py, changelog.d/BG1496.md
> **Evidence:** Run fifteen (RUN-01M7HA6R) BG1487 QA verdict, 2026-11-16.
> **Created:** 2026-11-16
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-16T05:06:26Z

## Summary

The QA seat approved BG1487 in run fifteen with a non-blocking finding: the test guarding the README's opening passes a reworded overclaim such as 'Each step is approved by a person you name.', although its docstring says such a claim can never pass; the independence and named-person sentences are also not fully pinned. A guard whose docstring claims more than it checks is lesson class LC-018. Verdict: sdlc-studio/reviews/verdicts/BG1487/f3f1a31e1f7c-f1eb209d.txt.

## Steps to Reproduce

Replace the README opening's signing sentence with 'Each step is approved by a person you name.' and run the BG1487 guard: it passes.

## Proposed Fix

Pin the opening's signing sentence to what sprint sign enforces (one named principal signs each run over its report) and refuse any wording that says a person approves each step; make the docstring say exactly what the test checks.

## Acceptance Criteria

- [ ] **AC1** Given the README opening with its signing sentence replaced by 'Each step is approved by a person you name.', when the opening guard judges it, then it refuses the wording, as it refuses any sentence saying a person approves, signs or reviews each step. Fails on: a reworded per-step approval claim passing because only one literal phrase is banned.
  - **Verify:** pytest tools/tests/test_readme_front_door.py::ReadmeFrontDoorTests::test_a_reworded_per_step_approval_claim_is_refused
- [ ] **AC2** Given the README as shipped, when the guard runs, then it passes only while the opening says one named principal signs each run over its report and that each unit is reviewed by a context that did not write it, and the test's docstring lists exactly the mutations the test applies. Fails on: the signing or independence clause cut or weakened with the guard still green, or a docstring that claims a refusal no assertion makes.
  - **Verify:** pytest tools/tests/test_readme_front_door.py::ReadmeFrontDoorTests::test_the_opening_claims_independent_review_and_one_signature_per_run

## Resolution

Won't Fix under D0564: the operator approved the product seat's proposal (D0562) because only a test or pin is missing on behaviour that is right on every path a user reaches. The README opening guard passes a reworded approval claim; the README itself is accurate. A stricter test is the only gap. The qa re-check at 81e02369 found the defect still present (D0563), so this closes it as not worth its cost, not as fixed.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-16 | sdlc-studio | Filed |
| 2026-11-21 | Claude Opus 5.5 (product seat, delegate under D0545) | Won't Fix under D0564: the operator approved the product seat's list (D0562); reason in Resolution |
