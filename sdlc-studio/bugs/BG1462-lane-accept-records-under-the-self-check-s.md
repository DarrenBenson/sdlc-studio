# BG1462: lane accept records under the self-check's agent author and critic.py record then warns that author lacks the holder (role) form

> **Status:** Open
> **Severity:** Low
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/lib/lanes.py, .claude/skills/sdlc-studio/scripts/critic.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_critic.py, .claude/skills/sdlc-studio/scripts/tests/test_lane_land.py
> **Evidence:** Run thirteen, US1058 round-2 accept, 2026-11-15.
> **Created:** 2026-11-15
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-15T18:01:58Z

## Summary

`sprint.py lane accept` records a verdict under the author of the unit's latest self-check unless `--author` is given. When `lane land` recorded that self-check, the author is the builder's agent id (for example agent-afbd3d2a94a3f7d31), so every accept prints critic.py record's warning that the author lacks the `<holder> (<role>)` form and that the retro cannot score its repairs as a seat's. The tool's own default produces the warning on every accept; the operator cannot act on it without hand-supplying an author.

## Steps to Reproduce

1. Land a lane with `sprint.py lane land`.
2. Record its review with `sprint.py lane accept --unit <id> --verdict <file> --reviewer <name>`.
3. See the WARNING line naming the agent author.

## Proposed Fix

Have `lane land` record the self-check under the builder seat `lane brief --seat` recorded, in the holder (role) form, keeping the agent id as a separate field, so accept's default author is a seat the retro can score.

## Acceptance Criteria

- [ ] **AC1** Given a lane whose brief recorded its builder seat with `lane brief --seat`, landed from an `agent-<id>` worktree, when `sprint.py lane land` records the unit's self-check, then the self-check's author is that seat in the `<holder> (<role>)` form and the agent id is kept in a field of its own. Fails on: the agent id recorded as the author, or the agent id lost.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lane_land.py::LaneLandTests::test_the_land_records_the_self_check_under_the_builder_seat
- [ ] **AC2** Given that landed unit, when `sprint.py lane accept --unit <id> --verdict <file> --reviewer <name>` runs with no `--author`, then the verdict is recorded against the builder seat and the output carries no warning that the author lacks the `<holder> (<role>)` form. Fails on: the default author still producing the warning on every accept.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lane_land.py::LaneLandTests::test_an_accept_after_the_land_prints_no_author_form_warning

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-15 | sdlc-studio | Filed |
