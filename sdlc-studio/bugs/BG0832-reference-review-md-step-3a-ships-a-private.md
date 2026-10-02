# BG0832: reference-review.md step 3a ships a private project's consultation cast as its example, names amigos with no resolver, and the neutrality lane misses it

> **Status:** Fixed
> **Groomed:** 2026-10-01 (D0291) - premise reproduced at HEAD: reference-review.md:279-281 lists `Darren (scope, priorities), Cora (API shape, errors), Webapp Dev ..., HA ...` and line 803 `"stale": ["Webapp Dev"]`; `check_neutrality.py` prints `no blocklisted project names` and exits 0. Narrowed to the doc fix: AC2 (widen the neutrality lane) dropped as a new refusal (D0291), and help/consult.md:56 holds (Sarah Chen is in persona-index-template only, not an amigo card)
> **Severity:** Medium
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/reference-review.md, tools/tests/test_lean_review_consult_neutral.py, changelog.d/BG0832.md
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

Replace the step 3a example and the JSON sample's names with neutral sample roles (e.g. a product owner, an API consumer, an operator), and name `persona_resolve.py resolve-consult` where the step means the amigos. No lane is widened.

## Acceptance Criteria

- [ ] **AC1** Given the shipped `reference-review.md`, when step 3a and the review JSON sample are read, then they name only sample roles (none of `Darren`, `Cora`, `Webapp Dev`, `HA`) and step 3a resolves the amigos through `persona_resolve.py`. Fails on: HEAD lines 279-281 and 803
  - **Verify:** pytest tools/tests/test_lean_review_consult_neutral.py::ReviewConsultNeutralTests::test_step_3a_names_sample_roles
  - **Verified:** yes (2026-10-01)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-28 | sdlc-studio | Filed |
