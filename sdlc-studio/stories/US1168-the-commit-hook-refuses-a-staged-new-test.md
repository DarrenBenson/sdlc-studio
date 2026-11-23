# US1168: The commit hook refuses a staged new test module with no `test-census-subject` marker

> **Status:** Draft
> **Risk-class:** high
> **Delivers:** CR0671
> **Created:** 2026-11-15
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** tools/check_census_marker.py, tools/check_neutrality.py, tools/tests/test_census_marker_lane.py, tools/tests/test_lean_commit_lanes.py, changelog.d/US1168.md
> **Epic:** EP0312
> **Points:** 2
> **Persona:** Rowan Achterberg

## User Story

**As a** head of engineering whose teams take changes through a change board
**I want** the commit hook refuses a staged new test module with no `test-census-subject` marker
**So that** I know what each team's delivery costs per point and can hold it to a monthly budget

## Acceptance Criteria

- **AC1:** Given a staged new test module whose first 40 lines carry no `# test-census-subject:` line, when the pre-commit hook runs, then the census-marker check, run inside the `neutrality` lane's script `tools/check_neutrality.py`, fails that lane naming the module and the line to add.
  - **Verify:** pytest tools/tests/test_census_marker_lane.py::CensusMarkerLaneTests::test_a_new_module_without_the_marker_is_refused
- **AC2:** Given the same module with the marker, or an existing module modified without one, when the hook runs, then the `neutrality` lane passes.
  - **Verify:** pytest tools/tests/test_census_marker_lane.py::CensusMarkerLaneTests::test_a_marked_or_existing_module_passes
- **AC3:** Given `.githooks/pre-commit --list`, when it prints, then it lists 31 lanes as before, none added for the census-marker check, and the `neutrality` lane's rule names the marker.
  - **Verify:** pytest tools/tests/test_census_marker_lane.py::CensusMarkerLaneTests::test_the_check_adds_no_lane

## Notes

- Serves Abena Osei's End goal 3; delivers part of CR0671 (D0479).
- AC1 must fail on: no such lane, or a lane that names no module
- AC2 must fail on: a lane that refuses existing unmarked modules (gate.py:2524 notes only over a third of modules carry one)
- AC3 must fail on: a 32nd lane, or a `neutrality` rule that does not name the marker
- Regroomed under D0507 after D0495 dropped it from its first run: US0905 caps the lanes a commit runs at `COMMIT_LANE_CAP` 31 (`test_lean_commit_lanes.py`), and `.githooks/pre-commit` already declares 31 with `run`, so a new lane would be the 32nd. D0507 folds the check into an existing lane instead, so the cap is untouched and no lane is displaced: `tools/check_neutrality.py`, the one script the `neutrality` lane runs, calls `tools/check_census_marker.py`, which `test_lean_precommit_parallel.py` does not see as a second lane because the lane still runs one script.
- D0495 counted 311 test modules with no marker, so the check refuses only a staged NEW module (a file added by the commit), never an existing one.
- Reuse gate.py's `_CENSUS_SUBJECT` pattern and test_census.py's first-40-lines rule rather than a third parser.
- The new test carries `# test-census-subject: tools/check_census_marker.py`.
- This story owns the epic's only remaining bar: D0512 retires EP0312's run-six replay and before-and-after criteria.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-15 | sdlc-studio | Created via `new` (deterministic) |
| 2026-11-15 | Claude Opus 5.5 (run fourteen grooming, D0479) | Groomed: criteria with Verify lines, must-fail notes, Affects with the tests each change exercises and this unit's fragment |
| 2026-11-23 | Dani Okafor (engineering, BG1538) | Regroomed under D0495, D0507 and D0512: the check runs inside the `neutrality` lane's script so the lane count stays at 31, Affects now name `tools/check_census_marker.py`, `tools/check_neutrality.py` and `tools/tests/test_lean_commit_lanes.py`, the run-14 wave note and the Depends line on a finished unit are gone, AC3 pins no new lane, status left at Draft |
