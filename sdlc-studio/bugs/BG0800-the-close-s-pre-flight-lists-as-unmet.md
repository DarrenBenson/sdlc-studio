# BG0800: The close's pre-flight lists as unmet the goal verdict the same invocation records and the review anchor the close writes itself

> **Status:** In Progress
> **Created:** 2026-09-27
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_lean_close.py, changelog.d/BG0800.md
> **Severity:** Low
> **Points:** 1

## Summary

`sprint.py close --retro RETRO-0001 --goal-verdict achieved --note ...` on a fresh rc.1 project printed 'close pre-flight: 4 unmet prerequisite(s) of 5 reported - this is ALL of them', listing `[goal-verdict] the Sprint Goal is unjudged` and `[gate] review-current: no reviews/LATEST.md`, then recorded the verdict, said review-current names only what the close writes, and exited 0. A first-time user reads four blockers and a green exit.

## Steps to Reproduce

As BG0799, then read the first lines of the second close's output.

## Proposed Fix

Evaluate the pre-flight after applying what the invocation supplies (the goal verdict) and exempt the anchor the close's own review-anchor step writes, as the gate step already does.

## Acceptance Criteria

- [ ] **AC1** Given a run with a filled retro and no `reviews/LATEST.md`, when `sprint.py close --retro <R> --goal-verdict achieved --note <n>` runs, then the pre-flight lists neither `[goal-verdict]` nor `review-current`, and the close exits 0. Fails on: HEAD ('4 unmet prerequisite(s) of 5 reported' then exit 0)
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_close.py::PreflightTests::test_the_preflight_lists_nothing_this_invocation_answers
- [ ] **AC2** Given the same run and a bare `sprint.py close --retro <R>` with no verdict, then the pre-flight still lists `[goal-verdict]`. Fails on: dropping the goal-verdict item from the pre-flight altogether
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lean_close.py::PreflightTests::test_a_close_given_no_verdict_still_lists_it

## Notes

First-week friction, not a wrong outcome. Polish-note carry from Sprint 5 ('close pre-flight on a fresh init project prints validate: 3 errors and review-current'); re-measured at HEAD with the variant above. Ratchet: removes false items, adds no check.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-27 | sdlc-studio | Created via `new` (deterministic) |
| 2026-09-27 | sdlc-studio v6 planning | Created for v6.0.0 Sprint 6 from the seat planning (BG0800) |
