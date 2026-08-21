# US0674: revert-check runs as an ADVISORY gate lane that records its yield, so the decision to make it blocking rests on a number

> **Status:** Draft
> **Delivers:** CR0547
> **Created:** 2026-08-21
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/gate.py, .claude/skills/sdlc-studio/scripts/verify_ac.py, .claude/skills/sdlc-studio/scripts/tests/test_gate.py, tools/tests/test_check_spec_claims.py, AGENTS.md
> **Epic:** EP0217
> **Points:** 3
> **Persona:** Maya Okafor

## User Story

**As a** Maya Okafor
**I want** revert-check runs as an ADVISORY gate lane that records its yield, so the decision to make it blocking rests on a number
**So that** CR0547 is delivered by work that can be planned and checked

## Acceptance Criteria

- [ ] **AC1** Given a project running the gate, when `gate.py` executes, then `revert-check` runs as a named lane and REPORTS a unit whose verifiers stay green after the revert, naming each such criterion, while the gate's exit code is unchanged - the lane is ADVISORY and cannot fail a commit, per CR0547's own recommendation that the yield be measured before it blocks
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_gate.py::RevertCheckLaneTests::test_the_lane_reports_without_changing_the_exit_code
- [ ] **AC2** Given a unit whose verifiers DO go red after the revert, when the lane runs, then it reports nothing for that unit - the paired control, because a lane that names every unit put in front of it has measured nothing and its yield figure would be meaningless
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_gate.py::RevertCheckLaneTests::test_a_unit_whose_verifiers_go_red_is_not_reported
- [ ] **AC3** Given the lane running over a batch, when it completes, then it records its YIELD - how many units it examined and how many it would have refused - to a file, and that recorded pair CHANGES with the input rather than being a constant the test could not falsify
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_gate.py::RevertCheckLaneTests::test_the_recorded_yield_changes_with_the_input
- [ ] **AC4** Given the pre-commit lane roster AGENTS.md documents, when `tools/tests/test_check_spec_claims.py` runs, then it names `revert-check` and names it as ADVISORY - a lane absent from the roster is one nobody notices losing (LL0013), and a lane the roster miscategorises is one whose blocking status nobody can check
  - **Verify:** pytest tools/tests/test_check_spec_claims.py -k revert_check

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-21 | sdlc-studio | Created via `new` (deterministic) |
| 2026-08-21 | sdlc-studio | Groomed: acceptance criteria authored against the slice |
| 2026-08-21 | sdlc-studio | Goal review: AC1 made the lane BLOCKING against CR0547's own recommendation of advisory-first, and AC3 (`reports its cost`) could not fail on anything. Re-authored advisory, with a paired control and a falsifiable yield record. Operator ruling, 2026-08-21 |
