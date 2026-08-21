# US0674: revert-check runs as an ADVISORY gate lane that records its yield, so the decision to make it blocking rests on a number

> **Status:** Draft
> **Delivers:** CR0547
> **Created:** 2026-08-21
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Verification depth:** functional [[derived: criteria 4; plan rows 5; executed 5; killed 5; survived 0; not-run 0; entry point 2 of 4 criteria through the shipped CLI, 1 in-process; 1 undetermined (the named node could not be isolated) | fp 6b92263d7bba ]] (the lane's binding is proved by SELECTION at both ends - refused off-boundary, running on-boundary - and both halves of its report are asserted: a unit that goes red is silent, a unit that stays green is named, and the gate passes either way. Every test drives a THROWAWAY workspace: the lane reverts production files, and pointed at this repository it rewrote `verify_ac.py` underneath a parallel test run. NOT covered: the lane still reverts files in the live tree at a real push, which is the design and is the subject of a filed CR, not of this unit)
> **Affects:** .claude/skills/sdlc-studio/scripts/gate.py, .claude/skills/sdlc-studio/scripts/verify_ac.py, .claude/skills/sdlc-studio/scripts/tests/test_gate.py, tools/tests/test_check_spec_claims.py, AGENTS.md
> **Depends on:** US0671, US0672, US0673 - the lane wraps the check, so the check must exist and be correct first. D0149 also requires the two gate lanes to land LAST and in their own commit, so a mid-run lane's refusals cannot be confused with the run's own defects.
> **Epic:** EP0217
> **Points:** 3
> **Persona:** Maya Okafor

## User Story

**As a** Maya Okafor
**I want** revert-check runs as an ADVISORY gate lane that records its yield, so the decision to make it blocking rests on a number
**So that** CR0547 is delivered by work that can be planned and checked

## Acceptance Criteria

- [ ] **AC1** Given `gate.py --boundary push` or `--boundary release`, when it runs, then `revert-check` runs as a named lane and REPORTS a unit whose verifiers stay green, naming each such criterion, while the exit code is unchanged. Bound at the boundary and NOT per-commit, on `release-rehearsal`'s precedent: reverting and re-running per unit costs minutes against a per-commit gate already at 53s, and a lane whose cost is paid on every commit gets switched off
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_gate.py::RevertCheckLaneTests::test_the_lane_runs_at_the_boundary_and_not_per_commit
  - **Verified:** yes (2026-08-21)
- [ ] **AC2** Given a unit whose verifiers DO go red after the revert, when the lane runs, then it reports nothing for that unit - the paired control, because a lane that names every unit put in front of it has measured nothing and its yield figure would be meaningless
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_gate.py::RevertCheckLaneTests::test_a_unit_whose_verifiers_go_red_is_not_reported
  - **Verified:** yes (2026-08-21)
- [ ] **AC3** Given the lane running over a batch, when it completes, then it records its YIELD - how many units it examined and how many it would have refused - to a file, and that recorded pair CHANGES with the input rather than being a constant the test could not falsify
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_gate.py::RevertCheckLaneTests::test_the_recorded_yield_changes_with_the_input
  - **Verified:** yes (2026-08-21)
- [ ] **AC4** Given the pre-commit lane roster AGENTS.md documents, when `tools/tests/test_check_spec_claims.py` runs, then it names `revert-check` and names it as ADVISORY - a lane absent from the roster is one nobody notices losing (LL0013), and a lane the roster miscategorises is one whose blocking status nobody can check
  - **Verify:** pytest tools/tests/test_check_spec_claims.py -k revert_check
  - **Verified:** yes (2026-08-21)

## Test Plan

| Criterion | Mutant - the production change this test must fail on | Title |
| --- | --- | --- |
| AC1 | in `gate.py`, register `revert-check` in `DEFAULT_CHECKS` so it binds on every commit | Given `gate.py --boundary push` or `--boundary release`, when it runs, then `revert-check` runs as a named lane and REPORTS a unit whose verifiers stay green, naming each such criterion, while the exit code is unchanged. Bound at the boundary and NOT per-commit, on `release-rehearsal`'s precedent: reverting and re-running per unit costs minutes against a per-commit gate already at 53s, and a lane whose cost is paid on every commit gets switched off |
| AC2 | in `gate.py`, replace the `res.get("status") == "refused"` guard in `_revert_check` with `True`, so every examined unit is appended to `refused` | Given a unit whose verifiers DO go red after the revert, when the lane runs, then it reports nothing for that unit - the paired control, because a lane that names every unit put in front of it has measured nothing and its yield figure would be meaningless |
| AC3 | in `gate.py`, replace the accumulating write in `_record_revert_yield` with a constant `{"runs": 1, "examined": 0, "would_refuse": 0}` | Given the lane running over a batch, when it completes, then it records its YIELD - how many units it examined and how many it would have refused - to a file, and that recorded pair CHANGES with the input rather than being a constant the test could not falsify |
| AC3 | in `gate.py`, move `_REVERT_YIELD_REL` to a tracked path outside `.local/` | Given the lane running over a batch, when it completes, then it records its YIELD - how many units it examined and how many it would have refused - to a file, and that recorded pair CHANGES with the input rather than being a constant the test could not falsify |
| AC4 | in `tools/tests/test_check_spec_claims.py`, widen the paragraph read back to a 900-character window around the lane name, so a neighbouring row's wording satisfies it | Given the pre-commit lane roster AGENTS.md documents, when `tools/tests/test_check_spec_claims.py` runs, then it names `revert-check` and names it as ADVISORY - a lane absent from the roster is one nobody notices losing (LL0013), and a lane the roster miscategorises is one whose blocking status nobody can check |

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-21 | sdlc-studio | Created via `new` (deterministic) |
| 2026-08-21 | sdlc-studio | Groomed: acceptance criteria authored against the slice |
| 2026-08-21 | sdlc-studio | Goal review: AC1 made the lane BLOCKING against CR0547's own recommendation of advisory-first, and AC3 (`reports its cost`) could not fail on anything. Re-authored advisory, with a paired control and a falsifiable yield record. Operator ruling, 2026-08-21 |
| 2026-08-21 | sdlc-studio | Goal review round 2: bound at the push/release boundary rather than per-commit, on `release-rehearsal`'s precedent - a revert-and-run per unit is minutes against a 53s per-commit gate |
