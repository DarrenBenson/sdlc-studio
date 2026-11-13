# BG1408: sprint lane land's hook-refusal text and module docstring say the worktree and main are as they were, which is untrue after the replay, and _discard_own_artefacts is untested

> **Status:** Open
> **Severity:** Low
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/scripts/lib/lanes.py, .claude/skills/sdlc-studio/scripts/tests/test_lane_land.py, .claude/skills/sdlc-studio/scripts/tests/test_land_refusal_text.py, changelog.d/BG1408.md
> **Evidence:** RUN-01M78TKD, 2026-11-13: review land, BG1336 and BG1337
> **Created:** 2026-11-13
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5 (run eleven orchestrator); agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-13T01:12:41Z

## Summary

lanes.py:29-30 and 171-172 claim 'the staged change, the worktree and main are as they were'. The `_discard_own_artefacts` docstring's 'committed as staged' is untested (mutant `checkout HEAD -- rel` survives).

## Steps to Reproduce

Land a unit whose hook refuses.

## Proposed Fix

Correct the text and pin the discard.

## Acceptance Criteria

- [ ] **AC1** Given a hook refusal after the replay, when the text prints, then it states what is left. Fails on: the as-they-were claim.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_land_refusal_text.py::LandRefusalTextTests

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-13 | Claude Opus 5.5 (run eleven orchestrator) | Filed |
