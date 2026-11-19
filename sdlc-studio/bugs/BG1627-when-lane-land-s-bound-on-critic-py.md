# BG1627: When lane land's bound on critic.py brief fires, critic is killed and the mutation runner its replay started is left running

> **Status:** Open
> **Severity:** Medium
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/lib/lanes.py, .claude/skills/sdlc-studio/scripts/tests/test_lane_land.py, changelog.d/BG1627.md
> **Evidence:** run eighteen, 2026-11-19: hand-back of the lane six repair builder
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

- [ ] **AC1** The behaviour described is corrected: Run eighteen's repair of US1202 bounds the QA brief lane land asks for by `critic.BRIEF_TIMEOUT` (780s, above the replay's own 600s) and reports a timed-out...
- [ ] **AC2** Following the recorded steps no longer reproduces the defect: Shrink `critic.BRIEF_TIMEOUT` below the replay's run time in a fixture and run sprint.py lane land: the land stops, and the runner and its pytest children...
- [ ] **AC3** The proposed fix lands, pinned by a test: Start critic.py brief in its own process group and end the group (SIGTERM, then SIGKILL after a grace) when the bound fires, so the runner removes its scratch...

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-19 | sdlc-studio | Filed |
