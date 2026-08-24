# US0674: revert-check runs as an ADVISORY gate lane that records its yield, so the decision to make it blocking rests on a number

> **Status:** Draft
> **Closed with findings in:** BG0606 - the test-plan plan review REJECTed this unit's plan, and the plan-review gate was overridden at the close on the operator's recorded decision to carry it rather than repair it in this run. The rows are named in BG0606 and the tests that would bind them already exist.
> **Delivers:** CR0547
> **Created:** 2026-08-21
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Verification depth:** functional [[derived: criteria 10; plan rows 10; executed 10; killed 10; survived 0; not-run 0; retracted 1; entry point 4 of 10 criteria through the shipped CLI, 5 in-process; 1 undetermined (the named node could not be isolated) | fp 00c981b5c8d2 ]] (the lane's binding is proved by SELECTION at both ends - refused off-boundary, running on-boundary - and both halves of its report are asserted: a unit that goes red is silent, a unit that stays green is named, and the gate passes either way. Every test drives a THROWAWAY workspace: the lane reverts production files, and pointed at this repository it rewrote `verify_ac.py` underneath a parallel test run. NOT covered: the lane still reverts files in the live tree at a real push, which is the design and is the subject of a filed CR, not of this unit)
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

- [ ] **AC1** Given `gate.py --boundary push` or `--boundary release`, when it runs, then `revert-check` runs as a named lane and REPORTS a unit whose verifiers stay green, while the exit code is unchanged. Bound at the boundary and NOT per-commit, on `release-rehearsal`'s precedent: reverting and re-running per unit costs minutes against a per-commit gate already at 53s, and a lane whose cost is paid on every commit gets switched off
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
- [ ] **AC5** Given the yield file, when the lane writes it, then it is written under gitignored `sdlc-studio/.local/` - the pair is this repository's own working measurement, not a tracked artefact every consuming project inherits
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_gate.py::RevertCheckLaneTests::test_the_yield_is_written_under_local
  - **Verified:** yes (2026-08-24)
- [ ] **AC6** Given a unit whose verifiers stay green after the revert, when the lane reports it, then that unit is NAMED, and so is each criterion that stayed green, and the gate still PASSES - advisory means reported-and-not-blocking, and a lane that never fires and a lane that blocks are different failures
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_gate.py::RevertCheckLaneTests::test_a_unit_that_stays_green_is_named_without_blocking
  - **Verified:** yes (2026-08-24)
- [ ] **AC7** Given a unit the lane cannot examine at all, when the lane reports, then the failure LEADS its message rather than being dropped behind a clean-sweep sentence - an absence must not read as a pass, which is the rule the checked code enforces four times over
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_gate.py::RevertCheckLaneTests::test_a_unit_the_lane_cannot_examine_is_not_reported_as_a_clean_pass
  - **Verified:** yes (2026-08-24)
- [ ] **AC8** Given a real boundary run of the shipped `gate.py`, when it completes, then THE LANE has written the yield file and a second run accumulates into it - the lane's own use of the recorder, not the recorder in isolation
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_gate.py::RevertCheckLaneTests::test_the_boundary_lane_itself_writes_the_yield_file
  - **Verified:** yes (2026-08-24)
- [ ] **AC9** Given a unit the check REPORTS rather than measures, when the lane runs, then that unit is not counted as examined and the yield pair says so - a unit that silently vanishes from the message and from the pair biases the very number the decision to make this lane blocking rests on
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_gate.py::RevertCheckLaneTests::test_a_reported_unit_is_not_counted_as_examined
  - **Verified:** yes (2026-08-24)
- [ ] **AC10** Given more findings than the lane prints, when it truncates them, then it says how many it dropped - AC6's naming claim is BOUNDED by that remainder, and a silent truncation reads as "that was all of them"
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_gate.py::RevertCheckLaneTests::test_the_lane_says_how_many_findings_it_dropped
  - **Verified:** yes (2026-08-24)

## Test Plan

| Criterion | Mutant - the production change this test must fail on | Title |
| --- | --- | --- |
| AC1 | in `gate.py`, register `revert-check` in `DEFAULT_CHECKS` so it binds on every commit | Given `gate.py --boundary push` or `--boundary release`, when it runs, then `revert-check` runs as a named lane and REPORTS a unit whose verifiers stay green, while the exit code is unchanged. Bound at the boundary and NOT per-commit, on `release-rehearsal`'s precedent: reverting and re-running per unit costs minutes against a per-commit gate already at 53s, and a lane whose cost is paid on every commit gets switched off |
| AC2 | in `gate.py`, replace the `res.get("status") == "refused"` guard in `_revert_check` with `True`, so every examined unit is appended to `refused` | Given a unit whose verifiers DO go red after the revert, when the lane runs, then it reports nothing for that unit - the paired control, because a lane that names every unit put in front of it has measured nothing and its yield figure would be meaningless |
| AC3 | in `gate.py`, replace the accumulating write in `_record_revert_yield` with a constant `{"runs": 1, "examined": 0, "would_refuse": 0}` | Given the lane running over a batch, when it completes, then it records its YIELD - how many units it examined and how many it would have refused - to a file, and that recorded pair CHANGES with the input rather than being a constant the test could not falsify |
| AC4 | in `gate.py`, return `blocking: True` from `_revert_check`'s refused path, so the lane blocks while AGENTS.md's roster still calls it ADVISORY | Given the pre-commit lane roster AGENTS.md documents, when `tools/tests/test_check_spec_claims.py` runs, then it names `revert-check` and names it as ADVISORY - a lane absent from the roster is one nobody notices losing (LL0013), and a lane the roster miscategorises is one whose blocking status nobody can check |
| AC5 | in `gate.py`, move `_REVERT_YIELD_REL` to a tracked path outside `.local/` | Given the yield file, when the lane writes it, then it is written under gitignored `sdlc-studio/.local/` - the pair is this repository's own working measurement, not a tracked artefact every consuming project inherits |
| AC6 | in `gate.py`, drop the `named.append(...)` for a refused unit in `_revert_check`, so a stays-green unit is counted and never named | Given a unit whose verifiers stay green after the revert, when the lane reports it, then that unit is NAMED, and so is each criterion that stayed green, and the gate still PASSES - advisory means reported-and-not-blocking, and a lane that never fires and a lane that blocks are different failures |
| AC7 | in `gate.py`, swallow the per-unit exception into `named` and drop `named` on the no-refusal path | Given a unit the lane cannot examine at all, when the lane reports, then the failure LEADS its message rather than being dropped behind a clean-sweep sentence - an absence must not read as a pass, which is the rule the checked code enforces four times over |
| AC8 | in `gate.py`, delete the `_record_revert_yield(root, examined, len(refused))` call from `_revert_check` | Given a real boundary run of the shipped `gate.py`, when it completes, then THE LANE has written the yield file and a second run accumulates into it - the lane's own use of the recorder, not the recorder in isolation |
| AC9 | in `gate.py`, move the `continue` for a reported unit below `examined += 1` in `_revert_check`, so a unit that measured nothing is counted as examined | Given a unit the check REPORTS rather than measures, when the lane runs, then that unit is not counted as examined and the yield pair says so - a unit that silently vanishes from the message and from the pair biases the very number the decision to make this lane blocking rests on |
| AC10 | in `gate.py`, return `"; ".join(items[:3])` from `_first_three` with no remainder, so a truncated finding list reads as the whole one | Given more findings than the lane prints, when it truncates them, then it says how many it dropped - AC6's naming claim is BOUNDED by that remainder, and a silent truncation reads as "that was all of them" |

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-21 | sdlc-studio | Created via `new` (deterministic) |
| 2026-08-21 | sdlc-studio | Groomed: acceptance criteria authored against the slice |
| 2026-08-21 | sdlc-studio | Goal review: AC1 made the lane BLOCKING against CR0547's own recommendation of advisory-first, and AC3 (`reports its cost`) could not fail on anything. Re-authored advisory, with a paired control and a falsifiable yield record. Operator ruling, 2026-08-21 |
| 2026-08-21 | sdlc-studio | Goal review round 2: bound at the push/release boundary rather than per-commit, on `release-rehearsal`'s precedent - a revert-and-run per unit is minutes against a 53s per-commit gate |
