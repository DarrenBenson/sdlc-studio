# BG0832: reference-review.md step 3a ships a private project's consultation cast as its example, names amigos with no resolver, and the neutrality lane misses it

> **Status:** Open
> **Severity:** Medium
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/reference-review.md, .claude/skills/sdlc-studio/help/consult.md, tools/check_neutrality.py, tools/tests/test_lean_review_consult_neutral.py, changelog.d/BG0832.md, tools/tests/test_check_neutrality.py
> **Evidence:** BG0816 builder hand-back and review; HEAD 7e53a438 reference-review.md lines 279-280 and 799
> **Created:** 2026-09-28
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-09-28T16:26:36Z

## Summary

reference-review.md:279-280 (step 3a, Persona Consultation) gives as its example the consultation guide of a private consuming project: an operator's first name and three of that project's agent and service names, and reference-review.md:799 repeats one in a JSON sample. The same step names amigos while loading only the project persona index, with no `persona_resolve.py` call. tools/`check_neutrality.py` passed it. help/consult.md:56 says `consult sarah-chen` is not the Product amigo, though `resolve-consult` by role may return that card.

## Steps to Reproduce

Read reference-review.md step 3a; run tools/`check_neutrality.py`: exit 0.

## Proposed Fix

Replace the example with neutral sample roles, name the resolver where the step means the amigos, correct help/consult.md:56, and add the leaked names' shape (a consultation guide's cast) to the neutrality lane's fixture.

## Acceptance Criteria

- [ ] **AC1** Given the shipped skill docs, then step 3a's example names only sample roles and the step resolves amigos through `persona_resolve.` Fails on: HEAD lines 279-280
  - **Verify:** pytest tools/tests/test_lean_review_consult_neutral.py::ReviewConsultNeutralTests::test_step_3a_names_sample_roles
- [ ] **AC2** Given a doc carrying a consultation-guide cast line, when `check_neutrality` runs, then it fails naming the line. Fails on: HEAD, which passes
  - **Verify:** pytest tools/tests/test_lean_review_consult_neutral.py::ReviewConsultNeutralTests::test_the_neutrality_lane_catches_a_cast_line

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-28 | sdlc-studio | Filed |
