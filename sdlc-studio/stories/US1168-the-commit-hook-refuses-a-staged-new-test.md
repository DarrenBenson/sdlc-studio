# US1168: The commit hook refuses a staged new test module with no `test-census-subject` marker

> **Status:** Draft
> **Risk-class:** standard
> **Delivers:** CR0671
> **Created:** 2026-11-15
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .githooks/pre-commit, tools/tests/test_precommit_lane_order.py, tools/tests/test_census_marker_lane.py, changelog.d/US1168.md
> **Epic:** EP0312
> **Points:** 2
> **Persona:** Rowan Achterberg

## User Story

**As a** head of engineering whose teams take changes through a change board
**I want** the commit hook refuses a staged new test module with no `test-census-subject` marker
**So that** I know what each team's delivery costs per point and can hold it to a monthly budget

## Acceptance Criteria

- **AC1:** Given a staged new test module whose first 40 lines carry no `# test-census-subject:` line, when the pre-commit hook runs, then a census-marker lane fails naming the module and the line to add.
  - **Verify:** pytest tools/tests/test_census_marker_lane.py::CensusMarkerLaneTests::test_a_new_module_without_the_marker_is_refused
- **AC2:** Given the same module with the marker, or an existing module modified without one, when the hook runs, then the lane passes.
  - **Verify:** pytest tools/tests/test_census_marker_lane.py::CensusMarkerLaneTests::test_a_marked_or_existing_module_passes
- **AC3:** Given `.githooks/pre-commit --list`, when it prints, then the new lane is listed with its rule and remedy.
  - **Verify:** pytest tools/tests/test_census_marker_lane.py::CensusMarkerLaneTests::test_the_lane_is_listed

## Notes

- Serves Abena Osei's End goal 3; delivers part of CR0671 (D0479).
- AC1 must fail on: no such lane, or a lane that names no module
- AC2 must fail on: a lane that refuses existing unmarked modules (gate.py:2524 notes only over a third of modules carry one)
- AC3 must fail on: a lane run outside the hook's `run` helper, which --list reads
- Lanes are declared with `run` (.githooks/pre-commit:222-510); --list reads them (:14-20); test_precommit_lane_order.py pins the order. Reuse gate.py's `_CENSUS_SUBJECT` pattern (:2476) and test_census.py's first-40-lines rule rather than a third parser.
- Every new test module in run fourteen should carry the marker from its first commit, since this lane lands in wave 2.
- The new test carries `# test-census-subject: .githooks/pre-commit`.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-15 | sdlc-studio | Created via `new` (deterministic) |
| 2026-11-15 | Claude Opus 5.5 (run fourteen grooming, D0479) | Groomed: criteria with Verify lines, must-fail notes, Affects with the tests each change exercises and this unit's fragment |
