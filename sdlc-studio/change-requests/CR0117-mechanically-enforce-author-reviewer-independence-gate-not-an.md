# CR-0117: Mechanically enforce author != reviewer (independence gate), not an honour-system convention

> **Status:** Complete
> **Priority:** High
> **Type:** Improvement
> **Date:** 2026-06-25
> **Created-by:** sdlc-studio file

## Summary

RFC0020's Three Amigos consult (Product/Engineering/QA, independent) unanimously named this the load-bearing prerequisite for any persona-shaped delegation - and it is valuable standalone, hardening the EXISTING independent critic. Today critic.py records a reviewer string but never proves reviewer != author; the sprint loop only asserts in prose that 'a sub-agent that did not write the diff judges it'. Under token pressure a prose invariant is silently violated. Make it mechanical: stamp an author identity (the authoring seat / delegation instance id) on a unit when its diff/tests are produced, and have the conformance gate hard-fail any unit whose critic verdict reviewer id equals its author id. Independence you cannot verify is independence you do not have. This holds whether workers are persona-framed or generic - the independence floor survives --skip-personas.

## Acceptance Criteria

- [x] critic.py record requires an --author (authoring seat/delegation id) and records both author and reviewer on the unit verdict
- [x] the conformance gate hard-fails a unit whose recorded critic reviewer id equals its author id (self-review blocked at the Done gate); a distinct reviewer passes
- [x] the check is independent of persona presence - it applies to generic workers too (independence is the floor, not a persona feature)
- [x] unit tests: reviewer==author blocks, reviewer!=author passes, missing author is flagged; documented in reference-sprint.md + the critic docs; CHANGELOG entry

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-06-25 | audit | Raised |
