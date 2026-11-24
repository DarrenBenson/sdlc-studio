# BG1594: sprint lane land records the builder's agent id as the self-check author instead of the building seat, so lane accept writes a verdict row the retro cannot score as a seat's

> **Status:** Open
> **Supersedes:** BG1462
> **Severity:** Low
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/lib/lanes.py, .claude/skills/sdlc-studio/scripts/tests/test_lane_accept.py, .claude/skills/sdlc-studio/scripts/tests/test_lane_land.py, changelog.d/BG1594.md
> **Evidence:** lane accept US1317, 2026-11-18: 'critic.py record: WARNING: author agent-adf464901f9fa8e86 lacks the <holder> (<role>) form'.
> **Created:** 2026-11-18
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-18T16:19:48Z

## Summary

For US1316 and US1317 in run seventeen, `sprint lane land` recorded the self-check (under the worktree directory name when no `--author` is given, `lib/lanes.py` `author or lane.name`), and `sprint lane accept` then recorded the APPROVE with author 'agent-adf464901f9fa8e86' and warned that it lacks the `<holder> (<role>)` form. The lane brief names the building seat (Dani Okafor (engineering)) and says the review brief's record command names it as the author, but the land does not carry it through.

## Steps to Reproduce

Land a unit with `sprint lane land`, then `sprint lane accept --unit <id> --verdict <file> --reviewer 'Sam Eriksson (qa)'`: the record warns that the author agent-<id> lacks the `<holder> (<role>)` form.

## Proposed Fix

Record the lane brief's building seat as the self-check author at land, and have lane accept read it, so the verdict row names the seat.

## Acceptance Criteria

- [ ] **AC1** Given a unit landed with `sprint lane land` from a worktree whose directory is not a seat name and no `--author`, when the self-check is recorded, then its author is the building seat of the lane brief in `holder (role)` form, not the worktree directory name or agent id. Fails on: `lanes._steps` records `author or lane.name`, so the self-check author is the directory name.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lane_land.py::LaneLandTests::test_the_self_check_is_recorded_under_the_briefed_building_seat
- [ ] **AC2** Given that landing, when `sprint lane accept --unit <id> --verdict <file> --reviewer 'Sam Eriksson (qa)'` runs with no `--author`, then the verdict row names the building seat in `holder (role)` form and `critic.py record` prints no `lacks the <holder> (<role>) form` warning. Fails on: accept reads the self-check author back, so the row carries `agent-<id>` and the warning prints.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lane_accept.py::LaneAcceptTests::test_an_accept_after_a_land_names_the_building_seat_and_prints_no_author_warning
- [ ] **AC3** Given a land with an explicit `--author 'Dani Okafor (engineering)'`, when it is accepted, then that author is kept and the brief's seat does not override it (the control beside AC1). Fails on: a fix that ignores `--author`.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lane_land.py::LaneLandTests::test_an_explicit_author_wins_over_the_briefed_seat
- [ ] **AC4** Given `lane land` then `lane accept` with no `--author`, when the verdict is recorded, then it is under the building seat in holder (role) form, the agent id kept as a separate field, and `critic.py record` prints no author-form warning (carried from BG1462). Fails on: the agent id is the only author on the row and no separate field keeps it.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lane_accept.py::LaneAcceptTests::test_the_agent_id_is_kept_in_its_own_field_beside_the_seat_author

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-18 | sdlc-studio | Filed |
| 2026-11-24 | Sam Eriksson (qa) | Groomed for run twenty-six: four executable criteria (seat at land, seat at accept, explicit author as control, agent id kept apart; AC4 is BG1462's, carried); Affects gains lib/lanes.py where land picks `author or lane.name` and accept reads it back; 2 pts to 3 since the fix spans land, accept and the verdict row's field set |
