# BG0239: The gate budget records a full-cost total when a unit suite was invoked but ran almost nothing

> **Status:** Fixed
> **Verification depth:** functional - the import-failure case is driven through the REAL hook in a throwaway repo (the harness built for the docs-only fix), asserting the total stays out of the series and that the skip is announced. Nine mutants, all killed; H1 restores the pre-fix behaviour exactly and is caught.
> **Severity:** Low
> **Points:** 2
> **Affects:** .githooks/pre-commit,tools/gate_timing.py,tools/tests/test_gate_timing.py,tools/tests/test_precommit_budget_recording.py
> **Created:** 2026-07-21
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1

## Summary

The pre-commit hook sets `suites_ran`=1 once the suite lane has been invoked, not once the suite has run its scope. A commit where a test module fails to import still takes that branch, so a run that executed a fraction of the tests is recorded as this commit's gate cost. Measured by the adversarial review of RUN-01KY1WCR: an import failure produced '73s of a 120s budget (baseline 99s), -26% since'. That is the same magnitude as the ~28% ratchet the lane exists to expose, in the opposite direction, so a broken suite reads as an improvement. Strictly milder than the docs-only hole fixed in the same sprint - that one recorded 9-14s runs and was fail-open in the ordinary path, this one needs a broken suite - and the reviewer agreed it should be tracked rather than patched at close time, on the evidence that three consecutive close-time repairs in that sprint each manufactured the next finding.

## Acceptance Criteria

- [x] **AC1:** A commit whose test module failed to import does not enter the budget series, and
      the skip is announced rather than silent. Driven through the REAL hook in a throwaway repo.
      **Verify:** shell python3 -m unittest discover -s tools/tests -p test_precommit_budget_recording.py
- [x] **AC2:** A suite that ran its whole scope and FAILED is still recorded, because the cost was
      paid whatever the verdict. This is the positive control that stops AC1 being satisfied by a
      hook that simply records nothing.
      **Verify:** shell python3 -m unittest discover -s tools/tests -p test_precommit_budget_recording.py
- [x] **AC3:** The scope decision is taken on a loader-error fact and a test-count floor, never on
      the run's duration, so a genuine speed-up is never discarded as implausible. The floor is
      pinned two-sided so moving it fails rather than silently widening what counts as a full run.
      **Verify:** shell python3 -m unittest discover -s tools/tests -p test_gate_timing.py

## Steps to Reproduce

1. Break a module in the skill suite so it fails to import. 2. Stage a scripts/ change and commit. 3. The skill-tests lane FAILs fast, `suites_ran` is still set, and the hook records the short total. 4. Observe the budget line report a large negative drift against the baseline.

## Proposed Fix

Record the total only when the suite lane reports a plausible scope - for example when its own recorded duration is within a band of its history, or when the runner reports a test count at or above a floor. Whatever the signal, it must distinguish 'ran and failed' (which SHOULD be recorded, since the cost was paid) from 'barely ran'.

## Resolution

`gate_timing.scope` now decides whether a run may enter the budget series, and the hook records
the total only when it says yes. The refusal is printed, never silent.

**The filed fix offered two signals and one of them is a trap.** "Whether its own recorded duration
is within a band of its history" is circular - it judges duration by duration - and it fails in the
direction that matters most: EP0093 took a commit from 196.7s to 99s, and any plausibility band
over prior history would have rejected that real improvement as implausible and discarded it. A
measurement rule that throws away genuine progress is worse than the bug. So scope is judged on
what the run DID, never on how long it took:

1. **A loader error.** A module that failed to import is the filed reproduction exactly. It is a
   fact rather than a threshold, so it needs no history and is checked first - which matters,
   because with no history a count-based rule is blind.
2. **The test count against the historic peak**, floor 80%. Catches a lane that ran a fraction of
   its scope without erroring, which no single fact reveals. Deliberately generous: tests are
   legitimately deleted (US0284 deleted one), and a floor that fires on real deletions trains
   people to ignore it.

The count is recorded even when the run is refused, or one truncated run would poison the series
permanently: the peak could never recover, because the counts that would rebuild it are exactly
the ones being discarded.

"Ran and failed" is still recorded, per the filed requirement - the cost was paid whatever the
verdict. Only "barely ran" is excluded, and that distinction has its own positive-control test.

`run()` in the hook now stashes its output on the green path too; it previously discarded it, and
the count is only knowable from a passing run's output as well as a failing one's.

Nine mutants, all killed: six over the scope logic (including both floor directions and the
boundary off-by-one) and three over the hook wiring. H1 restores the pre-fix `record`
unconditionally and is caught by the import-failure test; H3 always claims a loader error and is
caught by two positive controls, so the refusal cannot become blanket.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-21 | sdlc-studio | Filed |
| 2026-07-21 | claude | Fixed: `gate_timing scope` gates the recording on a loader-error fact plus an 80% test-count floor, explicitly NOT on a duration band (which would have discarded EP0093's real 196.7s -> 99s improvement). Hook records the total only when scope passes, and says so when it does not. 9 mutants killed. |
