# BG1627: When lane land's bound on critic.py brief fires, critic is killed and the mutation runner its replay started is left running

> **Status:** Open
> **Severity:** Medium
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/lib/lanes.py, .claude/skills/sdlc-studio/scripts/tests/test_lane_land.py, changelog.d/BG1627.md, .claude/skills/sdlc-studio/scripts/tests/test_lane_land_brief_bound_group.py
> **Evidence:** round two of the engineering seat on US1202 (sdlc-studio/reviews/verdicts/US1202/a035ef15c560-e539f377.txt): when the brief bound fires, the stop advises critic.py brief --unit <id> --seat qa (lib/lanes.py around 323), but lane accept still refuses with exit 2 afterwards because no saved QA brief exists; the advice must name a command that saves the brief lane accept reads
> **Created:** 2026-11-19
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-19T17:50:37Z

## Summary

Run eighteen's repair of US1202 bounds the QA brief lane land asks for by `critic.BRIEF_TIMEOUT` (780s, above the replay's own 600s) and reports a timed-out brief as a named stop. If that outer bound still fires, subprocess kills only critic.py: the mutation runner the replay started, and its pytest children, are orphaned, and the replay's scratch copy is not removed. The same shape as BG1610, one layer down.

## Steps to Reproduce

Shrink `critic.BRIEF_TIMEOUT` below the replay's run time in a fixture and run sprint.py lane land: the land stops, and the runner and its pytest children outlive it.

## Proposed Fix

Start critic.py brief in its own process group and end the group (SIGTERM, then SIGKILL after a grace) when the bound fires, so the runner removes its scratch copy; pin it with a test that checks no child outlives the stop.

## Acceptance Criteria

- [ ] **AC1** Given `critic.BRIEF_TIMEOUT` shrunk below the replay's run time in a fixture, when `sprint.py lane land` runs and the bound fires, then it stops and no mutation runner or pytest child the replay started outlives the stop, and the replay's scratch copy is removed. Fails on: only critic.py is killed, so the runner and its pytest children keep running and the scratch copy stays.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lane_land_brief_bound_group.py::LandBriefBoundKillsReplayTests

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-19 | sdlc-studio | Filed |
| 2026-11-21 | Claude Opus 5.5 (qa seat, groom) | Acceptance criteria authored for planning (run twenty-one) |
