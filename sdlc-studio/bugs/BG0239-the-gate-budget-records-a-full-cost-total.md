# BG0239: The gate budget records a full-cost total when a unit suite was invoked but ran almost nothing

> **Status:** Open
> **Severity:** Low
> **Points:** 2
> **Affects:** .githooks/pre-commit,tools/gate_timing.py
> **Created:** 2026-07-21
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1

## Summary

The pre-commit hook sets `suites_ran`=1 once the suite lane has been invoked, not once the suite has run its scope. A commit where a test module fails to import still takes that branch, so a run that executed a fraction of the tests is recorded as this commit's gate cost. Measured by the adversarial review of RUN-01KY1WCR: an import failure produced '73s of a 120s budget (baseline 99s), -26% since'. That is the same magnitude as the ~28% ratchet the lane exists to expose, in the opposite direction, so a broken suite reads as an improvement. Strictly milder than the docs-only hole fixed in the same sprint - that one recorded 9-14s runs and was fail-open in the ordinary path, this one needs a broken suite - and the reviewer agreed it should be tracked rather than patched at close time, on the evidence that three consecutive close-time repairs in that sprint each manufactured the next finding.

## Steps to Reproduce

1. Break a module in the skill suite so it fails to import. 2. Stage a scripts/ change and commit. 3. The skill-tests lane FAILs fast, `suites_ran` is still set, and the hook records the short total. 4. Observe the budget line report a large negative drift against the baseline.

## Proposed Fix

Record the total only when the suite lane reports a plausible scope - for example when its own recorded duration is within a band of its history, or when the runner reports a test count at or above a floor. Whatever the signal, it must distinguish 'ran and failed' (which SHOULD be recorded, since the cost was paid) from 'barely ran'.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-21 | sdlc-studio | Filed |
