# US0671: revert-check reverts a unit's production files and REFUSES when its own verifiers stay green

> **Status:** Draft
> **Delivers:** CR0547
> **Created:** 2026-08-21
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/verify_ac.py, .claude/skills/sdlc-studio/scripts/tests/test_verify_ac.py
> **Epic:** EP0217
> **Points:** 5
> **Persona:** Maya Okafor

## User Story

**As a** Maya Okafor
**I want** revert-check reverts a unit's production files and REFUSES when its own verifiers stay green
**So that** CR0547 is delivered by work that can be planned and checked

## Acceptance Criteria

- [ ] **AC1** Given a unit whose production files are reverted to the run's base ref, when ONLY that unit's own declared `Verify:` selectors are run, then `verify_ac.py revert-check` exits non-zero and names each criterion that stayed green - green after the revert is the REFUSAL, because a test that passes without the change never reached it
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_verify_ac.py::RevertCheckTests::test_a_unit_whose_verifiers_stay_green_after_the_revert_is_refused
- [ ] **AC2** Given a unit whose tests genuinely exercise the shipped path, when the same revert-and-run happens, then the unit PASSES the check - the paired control, so the gate is shown to discriminate rather than to refuse everything put in front of it
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_verify_ac.py::RevertCheckTests::test_a_unit_whose_verifiers_go_red_after_the_revert_passes
- [ ] **AC3** Given BG0593 as it stood at commit 20de1d1c - four criteria green, four mutants recorded killed, and a production change no test reached - when the check runs against that tree, then it REFUSES it. A gate that cannot fail on the defect that motivated it is not evidence of anything
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_verify_ac.py::RevertCheckTests::test_the_bg0593_regression_case_is_refused
- [ ] **AC4** Given a criterion whose `Verify:` line names a selector that does not resolve, when the check runs, then it reports UNRESOLVED for that criterion and does NOT count it as red - a selector failing because it names nothing is not a test reaching the change, and counting it as one is how this gate would manufacture a false pass
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_verify_ac.py::RevertCheckTests::test_an_unresolvable_selector_is_unresolved_not_red

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-21 | sdlc-studio | Created via `new` (deterministic) |
| 2026-08-21 | sdlc-studio | Groomed: acceptance criteria authored against the slice |
