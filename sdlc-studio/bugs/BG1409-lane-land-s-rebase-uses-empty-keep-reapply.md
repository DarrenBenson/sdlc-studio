# BG1409: lane land's rebase uses --empty=keep --reapply-cherry-picks, so a commit a builder made that main already holds becomes an empty commit

> **Status:** Open
> **Severity:** Medium
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/lib/lanes.py, .claude/skills/sdlc-studio/scripts/tests/test_lane_land.py, .claude/skills/sdlc-studio/scripts/tests/test_land_empty_replay.py, changelog.d/BG1409.md
> **Evidence:** RUN-01M78TKD, 2026-11-13: review land, BG1337
> **Created:** 2026-11-13
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5 (run eleven orchestrator); agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-13T01:12:49Z

## Summary

lanes.py:212 applies the flags to builder commits too. This was a regression ruled non-blocking.

## Steps to Reproduce

Land a lane holding a commit equal to one on main.

## Proposed Fix

Apply the flags only to the replayed staged change.

## Acceptance Criteria

- [ ] **AC1** Given a builder commit that main already holds, when the lane lands, then no empty commit results. Fails on: an empty commit.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_land_empty_replay.py::LandEmptyReplayTests

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-13 | Claude Opus 5.5 (run eleven orchestrator) | Filed |
