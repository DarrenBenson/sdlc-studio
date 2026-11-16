# BG1513: lane return --agent cannot price a builder spawned from another project's session: it looks for the transcript only under the lane repository's own projects directory

> **Status:** Open
> **Severity:** Low
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/lib/meter_cursor.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_meter_cursor.py
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

- [ ] **AC1** The behaviour described is corrected: The website run's builders were spawned from the skill repository's session, so their transcripts live under that project's ~/.claude/projects directory.
- [ ] **AC2** The proposed fix lands, pinned by a test: Search every projects directory for the agent's transcript when the lane repository's own has none, or take an explicit --transcript path.

## Impact

A cross-repository run reports no cost for its lanes, so its cost per point is understated.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-16 | sdlc-studio | Filed |
