# BG1779: A repair's recreated worktree holds no approach note, so the solution review gate refuses its land

> **Status:** Open
> **Severity:** Low
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/lib/lanes.py, .claude/skills/sdlc-studio/scripts/tests/test_solution_review_land.py, changelog.d/BG1779.md
> **Evidence:** US1347's builder noticed it while building the land gate in run twenty-eight (RUN-01M8B7DJ, 2026-11-27).
> **Created:** 2026-11-27
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** RUN-01M8B7DJ - raised during the run, 2026-11-27T22:37:45Z

## Summary

`sprint lane` recreates a refused unit's worktree for its repair with `restore_for_repair` (lib/lanes.py), which restores the staged diff and the hand-in but not the unit's approach note in sdlc-studio/.local/lane/. With `review.solution_review` on, `sprint lane land` reads the note from the worktree's hand-in, so a repaired unit whose GO was recorded before the refusal is refused for a missing note, and its builder must find and copy the agreed note back by hand.

## Steps to Reproduce

1. Set `review.solution_review.min_points: 3` in a fixture project.
2. Land a 3-point unit with an agreed approach note and a recorded GO, and have its review rejected.
3. Recreate its worktree for the repair with `restore_for_repair`.
4. Run `sprint lane land`: it refuses, as the lane holds no approach note.

## Proposed Fix

`restore_for_repair` copies the unit's approach note back into the recreated worktree's sdlc-studio/.local/lane/, so the recorded GO still binds to the same digest; a test pins the note's digest across the round trip.

## Acceptance Criteria

- [ ] **AC1** The behaviour described is corrected: `sprint lane` recreates a refused unit's worktree for its repair with `restore_for_repair` (lib/lanes.py), which restores the staged diff and the hand-in but...
- [ ] **AC2** The proposed fix lands, pinned by a test: `restore_for_repair` copies the unit's approach note back into the recreated worktree's sdlc-studio/.local/lane/, so the recorded GO still binds to the same...

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-27 | sdlc-studio | Filed |
