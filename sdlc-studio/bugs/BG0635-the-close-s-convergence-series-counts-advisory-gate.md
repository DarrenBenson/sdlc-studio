# BG0635: the close's convergence series counts ADVISORY gate lanes as outstanding blockers, so the review-repair loop can never converge and every close eventually hits the round cap

> **Status:** Open
> **Severity:** Medium
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py
> **Created:** 2026-08-29
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

`loop_termination` short-circuits to CONVERGED when the latest attempt's outstanding count is zero, and its own comment says why: the cap read only the LENGTH, so a finished loop was refused, and raising the cap merely moves the number at which that happens. But the count it reads is `len(pre['blockers'])`, and `pre['blockers']` includes the gate lanes the very same pre-flight prints as `[gate, reported not blocking]`. This repository always carries four of them - constitution, doc-surface, disclosure and mutation - so the series can never reach zero, the converged branch is unreachable, and every close is stopped by the cap with the message 'the review-repair loop is NOT converging' while the real blocker set is empty. RUN-01M11MEP recorded 5, 5, 4, 4 with all ten units signed off, every rejection repaired and zero outstanding findings.

## Steps to Reproduce

1. Take a run whose real blockers are cleared but whose repo carries any advisory gate lane.
2. Run `sprint.py close --retro RETROxxxx` up to `review.max_rounds` times.
3. Each attempt records `outstanding` equal to the advisory-lane count, never 0.
4. The close stops with 'the review-repair loop is NOT converging' and 'Hand off with the outstanding set named' - while the outstanding set contains only lanes it has just described as not blocking.
5. Raising `review.max_rounds` does not help: the next attempt records the same non-zero count.

## Proposed Fix

Count only BLOCKING blockers into the convergence series. The pre-flight already distinguishes them - it prints `[gate, reported not blocking]` for the advisory ones - so the information is present at the point the count is taken and is simply not used. `loop_termination` itself is correct and needs no change; the defect is in what is handed to it. Assert the property rather than the instance: a pre-flight whose every blocker is non-blocking must record `outstanding` 0, so the converged branch its own comment describes becomes reachable.

## Acceptance Criteria

- [ ] **AC1** Given a pre-flight whose blockers are ALL advisory, when a close attempt is recorded, then its `outstanding` count is 0 and `loop_termination` returns not-stopped whatever the attempt count ||| pytest .claude/skills/sdlc-studio/scripts/tests/`test_sprint.py`::LoopConvergenceTests::`test_advisory_lanes_do_not_count_as_outstanding`
- [ ] **AC2** Given a pre-flight carrying one BLOCKING lane alongside advisory ones, when the attempt is recorded, then `outstanding` counts the blocking lane only - the positive control, without which counting nothing at all satisfies the row above ||| pytest .claude/skills/sdlc-studio/scripts/tests/`test_sprint.py`::LoopConvergenceTests::`test_a_blocking_lane_still_counts`
- [ ] **AC3** Given a run at its round cap whose real blockers are cleared, when `sprint.py close` runs as a SUBPROCESS, then it proceeds rather than reporting non-convergence ||| pytest .claude/skills/sdlc-studio/scripts/tests/`test_sprint.py`::LoopConvergenceTests::`test_a_converged_run_at_the_cap_closes`

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-29 | sdlc-studio | Filed |
