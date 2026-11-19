# BG1448: lane land spends its full hook run before a rebase conflict, and a replayed generated page merges into drift

> **Status:** Open
> **Severity:** Medium
> **Points:** 5
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/lib/lanes.py, .claude/skills/sdlc-studio/scripts/tests/test_lane_land_replay.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py, changelog.d/BG1448.md
> **Evidence:** Run twelve (RUN-01M7E52T) orchestrator friction log
> **Created:** 2026-11-15
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5 (run twelve orchestrator); agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-15T05:37:48Z

## Summary

Twice in run twelve `lane land` reported 'replayed the staged change onto main before the commit', ran the commit hooks (about 20 minutes), then refused: once on a rebase conflict in `sprint_report.py` the replay did not catch (US1150/US1151 after US0996), once on surface drift because the 3-way merge of two lanes' regenerated reference-scripts-surface.md kept both verb rows and one count line (BG1268 after US1155).

## Steps to Reproduce

Land lane A, which regenerates the surface page for a new verb; then land lane B, which regenerated it from the old base for another verb: the hook refuses on surface drift after its full run.

## Proposed Fix

Rebase the lane onto main before the hook run so a conflict refuses first, and regenerate the docgen pages after the replay (or name the regeneration in the refusal).

## Acceptance Criteria

- [ ] **AC1** Given a lane whose rebase onto main conflicts, when `lane land` runs, then it refuses before the commit hooks run. Fails on: a hook run spent first.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lane_land_replay.py::LaneLandReplayTests
- [ ] **AC2** Given two lanes that each regenerated the surface page, when the second lands, then its commit carries the page regenerated over both. Fails on: a drift refusal.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-15 | Claude Opus 5.5 (run twelve orchestrator) | Filed |
