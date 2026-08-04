# BG0517: the close-loop cap stops a loop that has already converged - it counts attempts before it looks at the outstanding set

> **Status:** Open
> **Severity:** High
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py
> **Evidence:** RUN-01KZ5YXM on 2026-08-04. `close_attempts` recorded, in order: {outstanding: 1, stages: [gate]} x4, then {outstanding: 0, stages: []} x2. The cap was raised from 4 to 6 under D0128 and the sixth round was refused on the same rule with an empty outstanding set.
> **Created:** 2026-08-04
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

`loop_termination` tests `len(attempts) >= cap` FIRST and returns, before any check of what the attempts contain. So a run whose outstanding set has reached ZERO - every blocker cleared, the next round certain to complete - is stopped with `the declared round cap is reached ... Hand off with the outstanding set named`, and the outstanding set it invites you to name is empty.

Observed on RUN-01KZ5YXM. Its recorded series was `outstanding: 1, 1, 1, 1, 0, 0` with stages `[gate] x4` then `[] x2`. The first four rounds were unactionable for a different reason (BG0516); the last two show the blockers gone. The loop had converged and the guard stopped it anyway, and raising the cap only moves the number at which a converged loop is refused.

The divergence detector beside it is the model of what this should be: it reads the SERIES and fires on three rounds of growth. The cap reads only the length.

## Steps to Reproduce

1. Drive a close to the cap with a blocker present - each round records `outstanding: 1`.
2. Clear the blocker. Run the close again: it records `outstanding: 0` and stops on the cap.
3. Raise `review.max_rounds` and repeat: it records another `outstanding: 0` and stops again at the new number.

## Proposed Fix

Check the outstanding set before the count. A loop whose latest round reports zero outstanding has converged and must not be stopped - there is nothing left to iterate on, and the next round is the one that completes the ceremony. Keep the cap for the case it was written for, a loop still carrying blockers after N rounds, and keep the divergence detector untouched. A test should pin the boundary directly: a series ending in 0 does not terminate however long it is.

## Acceptance Criteria

- [ ] The behaviour described is corrected: `loop_termination` tests `len(attempts) >= cap` FIRST and returns, before any check of what the attempts contain.
- [ ] The proposed fix lands, pinned by a test: Check the outstanding set before the count.

## Impact

A run that has done everything asked of it cannot be closed by the command built to close it, and the only sanctioned exits are a handoff that abandons the ceremony or raising a ceiling that will refuse again two rounds later. It also teaches the wrong lesson about caps: the operator learns to raise them, which is how a guard becomes a formality.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-04 | sdlc-studio | Filed |
