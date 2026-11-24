# BG1595: sprint lane brief --units joins comma-separated ids into one id and refuses it, instead of splitting on commas or saying the ids are space-separated

> **Status:** Open
> **Severity:** Low
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_lane_accept.py, .claude/skills/sdlc-studio/scripts/tests/test_lane_brief_budget.py, .claude/skills/sdlc-studio/scripts/tests/test_lane_land.py, changelog.d/BG1595.md
> **Evidence:** .local/run17/lane-meta.err, 2026-11-18.
> **Created:** 2026-11-18
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-18T16:20:04Z

## Summary

`sprint lane brief --units US1315,US1319,US1320` refused with 'REFUSED US1315US1319US1320: no artefact on disk resolves to this id': the commas are stripped and the ids run together. Space-separated ids work. Commit subjects and Affects use comma lists, so a comma list is the natural thing to type.

## Steps to Reproduce

Run `sprint.py lane brief --units US1315,US1319,US1320`: it refuses 'US1315US1319US1320'.

## Proposed Fix

Split --units values on commas as well as spaces, or refuse a comma list by naming the space-separated form.

## Acceptance Criteria

- [ ] **AC1** Given `sprint.py lane brief --units US1315,US1319,US1320` over three real units, when it runs, then it briefs the three ids and exits 0. Fails on: `_lane_unit_ids` keeps the comma list as one id and refuses `US1315,US1319,US1320`.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lane_brief_budget.py::LaneBriefBudgetTests::test_a_comma_separated_units_list_briefs_each_unit
- [ ] **AC2** Given `--units US1315 US1319,US1320` (a mix of space and comma), when it runs, then three ids are briefed in order, and a stray trailing comma or empty piece is dropped. Fails on: only whitespace splitting.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lane_brief_budget.py::LaneBriefBudgetTests::test_mixed_space_and_comma_units_split_in_order
- [ ] **AC3** Given the space-separated form that works today, when `--units US1315 US1319` runs, then it behaves as before (the control beside AC1). Fails on: a split that breaks the existing form.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lane_brief_budget.py::LaneBriefBudgetTests::test_a_space_separated_units_list_still_briefs_each_unit
- [ ] **AC4** Given `sprint.py lane land --worktree <w> --units US1315,US1319` naming two units of a landable lane, when it runs, then it lands both units as the space-separated form does. Fails on: the comma list is kept as one id, so the land refuses it as a unit it does not know.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lane_land.py::LaneLandTests::test_a_comma_separated_units_list_lands_each_unit

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-18 | sdlc-studio | Filed |
| 2026-11-24 | Sam Eriksson (qa) | Groomed for run twenty-six: executable criteria for the comma list, a mixed list and the unchanged space form; the fix splits in `_lane_unit_ids`, not refuses; Affects names the brief test module, which has the lane fixture |
| 2026-11-24 | orchestrator (delegate under D0545) | Affects widened for run twenty-six's SPB lane: AC4 added: `lane land --units` takes the same comma-separated list (D0561, fix in the unit rather than file a sibling) |
