# BG0517: the close-loop cap stops a loop that has already converged - it counts attempts before it looks at the outstanding set

> **Status:** Fixed
> **Severity:** High
> **Points:** 2
> **Verification depth:** functional
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

- [x] **AC1: a converged loop is never stopped, however long it has run.**
  - **Given** an attempt series whose latest round reports zero outstanding - every blocker
    cleared - and whose length is at or beyond the cap
  - **When** `loop_termination` judges it
  - **Then** it does NOT terminate, because there is nothing left to iterate on and the next
    round is the one that completes the ceremony. RUN-01KZ5YXM's series was `1, 1, 1, 1, 0, 0`:
    finished, and stopped.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::ConvergedLoopIsNotStoppedTests::test_a_series_ending_in_zero_outstanding_never_terminates
  - **Verified:** yes (2026-08-04)

- [x] **AC2: the cap still stops a loop that is still carrying blockers.**
  - **Given** an attempt series at the cap whose latest round still reports outstanding work
  - **When** it is judged
  - **Then** it terminates on the cap exactly as before, because that is the case the cap was
    written for - an unattended loop going round on work it is not clearing
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::ConvergedLoopIsNotStoppedTests::test_the_cap_still_stops_a_loop_that_is_not_converging
  - **Verified:** yes (2026-08-04)

- [x] **AC3: the divergence detector is untouched.**
  - **Given** a series that grows for three rounds running and ends with outstanding work
  - **When** it is judged
  - **Then** it still terminates on divergence, so the convergence exemption cannot be used to
    keep a loop alive that is re-breaking what the last round cleared
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::ConvergedLoopIsNotStoppedTests::test_divergence_still_terminates
  - **Verified:** yes (2026-08-04)

## Impact

A run that has done everything asked of it cannot be closed by the command built to close it, and the only sanctioned exits are a handoff that abandons the ceremony or raising a ceiling that will refuse again two rounds later. It also teaches the wrong lesson about caps: the operator learns to raise them, which is how a guard becomes a formality.

## Verification evidence

Functional. Three mutants executed, `__pycache__` purged and each child run under `python3 -B`,
anchors asserted unique, source restored byte-identical:

| Mutant | Result |
| --- | --- |
| move the converged check back below the cap test | killed |
| treat any zero ANYWHERE in the series as converged | killed |
| drop the divergence detector | killed |

The second is the one worth naming. Convergence is a fact about the LATEST round: a loop that
cleared everything and then broke it again is exactly the loop the cap exists for, and reading
`0 in counts` would let it run forever. A test pins `1, 0, 2, 3` as still terminating.

Driven on the real series that produced this bug: `loop_termination([1,1,1,1,0,0], cap=4)` now
returns `(False, '')` where it returned the round-cap refusal, while `[1,1,1,1]` still stops on
the cap and `[1,2,3,4]` still stops on divergence.

**The two cap raises are reverted.** D0128 said they would when this landed, and leaving them
would be the thing this bug is about - a guard whose number keeps moving is one nobody trusts.
`review.max_rounds` is gone from the project config and the default of 4 is back in force.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-04 | sdlc-studio | Filed |
