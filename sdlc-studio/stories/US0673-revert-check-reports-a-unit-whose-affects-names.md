# US0673: revert-check REPORTS a unit whose Affects names no production file rather than passing it

> **Status:** Review
> **Delivers:** CR0547
> **Created:** 2026-08-21
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Verification depth:** functional [[derived: criteria 2; plan rows 2; executed 2; killed 2; survived 0; not-run 0; entry point 2 of 2 criteria through the shipped CLI, 0 in-process | fp d39fb8daa9b6 ]] (both reported conditions are driven through the command and asserted on their own exit code, so an absence cannot read as a pass. NOT covered: a production path that exists but cannot be read)
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
  - **Verified:** yes (2026-08-21)
- [ ] **AC2** Given a unit whose `Affects` names a production file absent from the tree, when the check runs, then it reports the unresolvable path rather than silently reverting the subset it could resolve - a partial revert tests a change nobody described
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_verify_ac.py::RevertCheckTests::test_an_unresolvable_affects_path_is_reported
  - **Verified:** yes (2026-08-21)

## Test Plan

| Criterion | Mutant - the production change this test must fail on | Title |
| --- | --- | --- |
| AC1 | in `verify_ac.py`, drop the empty-`production` branch from `revert_check` so the check falls through and returns `pass` | Given a unit whose `Affects` names no production file at all - only test files, or only markdown - when the check runs, then it REPORTS that condition by name and does not pass the unit. Nothing to revert is not evidence that the tests reach anything, and an absence and a pass must not read the same |
| AC2 | in `verify_ac.py`, drop the `unresolvable` branch from `revert_check` and revert the subset that does resolve | Given a unit whose `Affects` names a production file absent from the tree, when the check runs, then it reports the unresolvable path rather than silently reverting the subset it could resolve - a partial revert tests a change nobody described |

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-21 | sdlc-studio | Created via `new` (deterministic) |
| 2026-08-21 | sdlc-studio | Groomed: acceptance criteria authored against the slice |
