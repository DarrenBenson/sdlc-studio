# US0679: The scope subscore stops counting a test file present only because the Affects convention requires it

> **Status:** Draft
> **Delivers:** CR0549
> **Created:** 2026-08-21
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/route.py, .claude/skills/sdlc-studio/scripts/tests/test_route.py
> **Epic:** EP0217
> **Points:** 3
> **Persona:** Maya Okafor

## User Story

**As a** Maya Okafor
**I want** The scope subscore stops counting a test file present only because the Affects convention requires it
**So that** CR0549 is delivered by work that can be planned and checked

## Acceptance Criteria

- [ ] **AC1** Given a unit whose `Affects` names at least one production file, when `scope` is computed, then a test file beside it does NOT count - the rule is stated as a rule: a test file is CONVENTIONAL when the same `Affects` also names production code, and counts otherwise
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_route.py::ScopeConventionTests::test_a_test_file_beside_production_code_does_not_count
- [ ] **AC2** Given a unit whose `Affects` names ONLY test files - a story about test scaffolding - when `scope` is computed, then those files DO count, because there the test file is the subject rather than the convention
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_route.py::ScopeConventionTests::test_a_units_own_test_subject_still_counts
- [ ] **AC3** Given the mixed case - a production file plus a test file for a DIFFERENT module - when `scope` is computed, then the stated rule decides it and the decision is asserted, because a rule with an undefined case is a rule somebody will resolve by guessing
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_route.py::ScopeConventionTests::test_the_mixed_case_is_decided_by_the_stated_rule

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-21 | sdlc-studio | Created via `new` (deterministic) |
| 2026-08-21 | sdlc-studio | Groomed: acceptance criteria authored against the slice |

| 2026-08-24 | sdlc-studio | RE-GROOMED against CR0549's second and third corrections after a pre-code goal review REJECTED the first attempt: the declared basis now reads `Points` and `Affects` breadth rather than whole-file complexity, measured to move `light` from 13% to 33%. |
