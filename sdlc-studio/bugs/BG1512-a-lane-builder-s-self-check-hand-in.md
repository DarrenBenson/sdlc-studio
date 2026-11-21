# BG1512: A lane builder's self-check hand-in is refused only after lane land has committed the unit, for surfaces, rulings and mutant results the brief names only in passing

> **Status:** Fixed
> **Severity:** Medium
> **Points:** 5
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/critic.py, .claude/skills/sdlc-studio/templates/agents/sdlc-builder.md, .claude/skills/sdlc-studio/scripts/tests/test_lane_land.py, .claude/skills/sdlc-studio/scripts/tests/test_lane_builder_brief.py, .claude/skills/sdlc-studio/scripts/tests/test_critic_self_check_record.py, .claude/skills/sdlc-studio/scripts/lib/lanes.py, changelog.d/BG1512.md
> **Created:** 2026-11-16
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-16T17:52:04Z

## Summary

In the website's 6.4 run all three lane builders wrote hand-ins `critic.py self-check record` refuses: surfaces such as 'page:commands.mdx' or 'page prose', rulings with prose after the word ('TRUE - ...', 'TRUE in substance', 'n/a'), mutant results 'SURVIVED' and 'control-green', and a mutant killed by a build check rather than a test in Affects. `sprint lane land` commits and fast-forwards main first, then refuses the record, so the orchestrator reshaped six hand-ins by hand. A docs-only unit's own pages are also no allowed surface, though they are where its claims live.

## Steps to Reproduce

1. Have a lane builder write a claims file with surface 'page:x.mdx' or ruling 'TRUE - evidence'.
2. Run sprint.py lane land: it commits and fast-forwards main, then prints 'self-check REFUSED and no brief written'.

## Proposed Fix

Validate the hand-in before the land commits (or give the builder a `self-check check` to run), print the allowed surfaces, rulings and results in the lane brief, and accept a page in the unit's Affects as a claim surface.

## Acceptance Criteria

- [ ] **AC1** Given a staged lane whose hand-in holds a claim `critic.py self-check record` refuses (surface 'page prose', ruling 'TRUE in substance' or result 'SURVIVED'), when `sprint.py lane land` runs, then it refuses before any commit, names each refused value with the allowed ones, and main and the worktree are as they were. Fails on: the unit committed and fast-forwarded first and the hand-in refused after.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lane_land.py::LaneLandTests::test_a_hand_in_the_record_would_refuse_stops_the_land_before_the_commit
  - **Verified:** yes (2026-11-21)
- [ ] **AC2** Given a lane brief written for a builder, when it is read, then it lists the allowed claim surfaces, rulings and mutant results word for word from the constants `critic.py` checks against. Fails on: a brief that names them in passing, or a list that drifts from what the record accepts.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lane_builder_brief.py::BuilderBriefTests::test_the_brief_lists_the_surfaces_rulings_and_results_the_record_accepts
  - **Verified:** yes (2026-11-21)
- [ ] **AC3** Given a docs-only unit whose Affects names a page, when its hand-in makes a claim whose surface is that page's path, then `self-check record` accepts it, and a claim on a page outside the unit's Affects is still refused. Fails on: a unit unable to cite the page its claims live in, or any path at all accepted as a surface.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic_self_check_record.py::SelfCheckRecordTests::test_a_page_in_the_unit_s_affects_is_a_claim_surface
  - **Verified:** yes (2026-11-21)
- [ ] **AC4** Given a staged lane with a hand-in the record accepts, when `lane land` runs, then it commits, fast-forwards main, records the self-check and writes the brief as before. Fails on: the earlier validation refusing or skipping a valid hand-in.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lane_land.py::LaneLandTests::test_each_landed_unit_gets_its_self_check_and_brief
  - **Verified:** yes (2026-11-21)

## Impact

Every lane land needs hand repair of the evidence it records, which is the hand-rolling the tooling exists to remove.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-16 | sdlc-studio | Filed |
