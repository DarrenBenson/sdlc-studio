# US0673: revert-check REPORTS a unit whose Affects names no production file rather than passing it

> **Status:** Draft
> **Delivers:** CR0547
> **Created:** 2026-08-21
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/verify_ac.py, .claude/skills/sdlc-studio/scripts/tests/test_verify_ac.py
> **Epic:** EP0217
> **Points:** 2
> **Persona:** Maya Okafor

## User Story

**As a** Maya Okafor
**I want** revert-check REPORTS a unit whose Affects names no production file rather than passing it
**So that** CR0547 is delivered by work that can be planned and checked

## Acceptance Criteria

- [ ] **AC1** Given a unit whose `Affects` names no production file at all - only test files, or only markdown - when the check runs, then it REPORTS that condition by name and does not pass the unit. Nothing to revert is not evidence that the tests reach anything, and an absence and a pass must not read the same
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_verify_ac.py::RevertCheckTests::test_a_unit_with_no_production_file_is_reported_not_passed
- [ ] **AC2** Given a unit whose `Affects` names a production file absent from the tree, when the check runs, then it reports the unresolvable path rather than silently reverting the subset it could resolve - a partial revert tests a change nobody described
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_verify_ac.py::RevertCheckTests::test_an_unresolvable_affects_path_is_reported

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-21 | sdlc-studio | Created via `new` (deterministic) |
| 2026-08-21 | sdlc-studio | Groomed: acceptance criteria authored against the slice |
