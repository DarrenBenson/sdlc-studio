# BG1538: US1168 cannot be built as written because the D0495 ruling was never written back to the story or its epic

> **Status:** Open
> **Severity:** Medium
> **Points:** 2
> **Affects:** sdlc-studio/stories/US1168-the-commit-hook-refuses-a-staged-new-test.md, sdlc-studio/epics/EP0312-the-commit-hook-runs-the-cheap-repo-wide.md, changelog.d/BG1538.md
> **Evidence:** audit AUDIT-2026-11-17, project profile, stories lens, survived 2 of 3 refute votes; observed at sdlc-studio/stories/US1168-the-commit-hook-refuses-a-staged-new-test.md Header (Status, Affects) and Notes lines 36-37; sdlc-studio/epics/EP0312-the-commit-hook-runs-the-cheap-repo-wide.md epic-level criteria 4 and 5
> **Created:** 2026-11-17
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-17T16:26:53Z

## Summary

Decision D0495 dropped US1168 (the census-marker commit lane) from run fourteen because it cannot land within its Affects. A new pre-commit lane makes 32 lanes against `COMMIT_LANE_CAP` of 31 in `tools/tests/test_lean_commit_lanes.py`, and each lane must run one script, so the story needs a new `tools/check_census_marker.py` and a ruled change to the cap. The decision says the story returns to Ready for a later run with that regroom. The story file still reads Status Draft, its Affects omits the new script and the cap test, its Revision History stops at the 2026-11-15 groom, and its Notes still say the lane lands in wave 2 of run fourteen. Nothing in the story, EP0312 or CR0671 names D0495, the cap or the 311 unmarked modules, so the next planner meets the same refusal the last builder did. Two epic-level criteria of EP0312 (the run-six replay in a throwaway clone and the before-and-after report reading) are also owned by no story.

## Steps to Reproduce

1. Read D0495 in `sdlc-studio/decisions.md` (line 509): US1168 needs a `tools/check_census_marker.py` script and a ruled cap change, and returns to Ready with that regroom.
2. Open `sdlc-studio/stories/US1168-the-commit-hook-refuses-a-staged-new-test.md`: Status is Draft, Affects lists neither `tools/check_census_marker.py` nor `tools/tests/test_lean_commit_lanes.py`, and the Notes say the lane lands in wave 2.
3. Search the US1168 story, the EP0312 epic and the CR0671 file for D0495, `check_census_marker` and `COMMIT_LANE_CAP`: there is no match.
4. Read `tools/tests/test_lean_commit_lanes.py` line 103: the cap is 31.
5. Read epic-level criteria 4 and 5 of EP0312 and the notes of US1167: the replay and the before-and-after reading are handed to the orchestrator with no Verify line and no unit.
6. Expected: the story carries the ruling and is buildable. Actual: a builder following the story as written is refused by the cap test.

## Proposed Fix

Regroom US1168 in its story file: add `tools/check_census_marker.py` and `tools/tests/test_lean_commit_lanes.py` to Affects, cite D0495 in the Notes with the lane-cap constraint and the count of unmarked modules, remove the run fourteen wave note, state which lane is displaced or which decision raises the cap, add a Revision History row, re-size the story and set its status as the regroom leaves it. In the EP0312 epic file, name the unit that owns epic-level criteria 4 and 5 or record the decision that retires them. No new test is needed for the paperwork itself: the regroomed story's own Verify lines and the existing cap test in `test_lean_commit_lanes.py` are what hold it, and `sprint plan` accepting the unit is the check.

## Acceptance Criteria

- [ ] **AC1** Given US1168 as dropped from 6.4 under D0495, when it is regroomed under D0507, then its criteria have the census-marker check run inside an existing commit-hook lane's script, the lane count stays at 31, and its `Depends on` line no longer names a finished unit. Fails on: a criterion that adds a 32nd lane, or the story still reading as it did when it was dropped.
  - **Verify:** manual read the records the criterion names and confirm each reads as stated; paperwork only, no test can pin it
- [ ] **AC2** Given EP0312's completion criteria, when the epic is corrected under D0512, then the run-six replay and the before-and-after report reading are marked retired with the decision named, and the epic's bar is US1168 alone. Fails on: either criterion left open with no owner.
  - **Verify:** manual read the records the criterion names and confirm each reads as stated; paperwork only, no test can pin it
- [ ] **AC3** Given the corrected story, when the planner's readiness report is run over US1168, then it lists US1168 as groomed. Fails on: US1168 refused as ungroomed or blocked.
  - **Verify:** manual read the records the criterion names and confirm each reads as stated; paperwork only, no test can pin it

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-17 | sdlc-studio | Filed |
