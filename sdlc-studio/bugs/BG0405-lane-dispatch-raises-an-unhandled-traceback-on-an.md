# BG0405: lane_dispatch raises an unhandled traceback on an unreadable run state, where a brief used to be issued

> **Status:** Open
> **Severity:** Medium
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py
> **Evidence:** Independent review of RUN-01KYNKDP: `sprint.py lane brief --units US0553` against a truncated run-state.json raises RunStateError out of lane_dispatch line 2131.
> **Created:** 2026-07-29
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1

## Summary

BG0391 widened the lane brief's seam scope to the open run's approved batch, and reads it with a bare `run_state.read(root)`. `run_state.read` RAISES on an unparseable file, by design - 'unreadable is not the same fact as absent'.

The seam computation immediately below it is wrapped in `_batch_seams` precisely because 'a seam read must never block a dispatch'. The new read sits above that guard, so a corrupt run state now produces an unhandled traceback where a brief used to be issued. Before this change `lane_dispatch` never touched run state at all.

The same class reaches `close_goal_judgement`, which is documented as never blocking a close and calls `run_state.lanes_in_flight` (and so `run_state.read`) unguarded.

## Steps to Reproduce

1. Truncate `sdlc-studio/.local/run-state.json`.
2. `python3 sprint.py lane brief --units US0553` -> RunStateError traceback.

## Proposed Fix

Put the read inside the same guard the seam computation already has: an unreadable run state means the batch scope is unknown, so fall back to the briefed units and SAY so in the brief. A lane brief must degrade, never crash - the operator running it is usually mid-restart, which is exactly when the state file is most likely to be damaged. Guard the reporting calls in `close_goal_judgement` for the same reason.

## Acceptance Criteria

- [ ] A lane brief over an unreadable run state is issued, with the seam scope reported as unknown rather than crashing.
- [ ] A readable run state still widens the scope to the approved batch.
- [ ] `close_goal_judgement` reports rather than raises when the run state cannot be read, matching its docstring.

## Impact

The lane brief is the command an operator runs to recover after a lane died - the moment a corrupt run state is most likely, and the moment a traceback is least useful.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-29 | sdlc-studio | Filed |
