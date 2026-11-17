# BG1513: lane return --agent cannot price a builder spawned from another project's session: it looks for the transcript only under the lane repository's own projects directory

> **Status:** Open
> **Severity:** Low
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/lib/run_state.py, .claude/skills/sdlc-studio/scripts/tests/test_lane_priced.py
> **Created:** 2026-11-16
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-16T17:52:19Z

## Summary

The website run's builders were spawned from the skill repository's session, so their transcripts live under that project's ~/.claude/projects directory. `sprint.py --root <web> lane return --agent <id>` warned 'no session transcript (*.jsonl) in the website project's directory' and left the lane unpriced. The same lookup leaves `critic.py record` printing 'verdict file provenance is unknown' for every website verdict in that run, because the reviewer's transcript sits under the skill repository's project directory.

## Steps to Reproduce

1. From project A's session, spawn a builder for a lane in repository B.
2. Run sprint.py --root B lane return --agent <id>: it warns that no transcript exists under B's projects directory and leaves the lane unpriced.

## Proposed Fix

Search every projects directory for the agent's transcript when the lane repository's own has none, or take an explicit --transcript path.

## Acceptance Criteria

- [ ] **AC1** Given a builder whose transcript lies under another project's directory in the harness's projects store, and none under the lane repository's own, when `sprint.py lane return --agent` names it, then the lane is priced from that transcript and the output names the directory it was read from. Fails on: a cross-repository lane left unpriced with a warning that no transcript exists.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lane_priced.py::LanePricedTests::test_an_agent_spawned_from_another_project_s_session_is_priced
- [ ] **AC2** Given a transcript for the agent under the lane repository's own project directory and another of the same name under a second project, when `lane return --agent` runs, then the lane repository's own is the one read. Fails on: the wider search preferring a foreign transcript over the local one.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lane_priced.py::LanePricedTests::test_the_lane_repository_s_own_transcript_wins_over_another_project_s
- [ ] **AC3** Given an agent id with no transcript under any project directory, when `lane return --agent` runs, then it warns naming the agent and every directory searched and records no priced cost. Fails on: a missing agent priced as nought, or a warning that still names only the lane repository's directory.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lane_priced.py::LanePricedTests::test_an_unknown_agent_warns_and_records_no_priced_cost

## Impact

A cross-repository run reports no cost for its lanes, so its cost per point is understated.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-16 | sdlc-studio | Filed |
