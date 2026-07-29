# BG0416: Reopening a unit does not retract its verification-depth claim, so the planner reads it as BUILT-NOT-CLOSED and forecasts it at zero points

> **Status:** Open
> **Severity:** Medium
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/transition.py, .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_transition.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py
> **Evidence:** BG0372 stands at Status Open, REOPENED at RUN-01KYNKDP's closing review because the fix delivered nothing, and still carries `> **Verification depth:** functional (tests red-first)` from the retracted Fixed. Planning the next sprint, `sprint plan` prints `excluded from the build forecast (BUILT-NOT-CLOSED, close them): BG0402, BG0359, BG0372` and forecasts 142 points against a 150-point batch. The 8 missing points are exactly those three units.
> **Created:** 2026-07-29
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1

## Summary

A reopen retracts the status and leaves the evidence claim standing.

BG0372 and BG0359 were reopened at the last close for the strongest possible reason: each was marked Fixed while delivering nothing. The reopen moved Status back to Open and wrote the finding into the revision history. It did not touch `Verification depth`, so each file still asserts it was verified to a functional tier by tests that ran red first - the exact claim the reopen exists to withdraw.

The planner then reads that field and concludes the unit is built and merely unclosed, so it excludes it from the build forecast. Planning a 150-point batch produces a 142-point forecast, and the eight-point gap is invisible unless a reader notices the exclusion line and knows why those three ids are on it.

The direction of the error is the bad one. A unit reopened for delivering nothing is not cheaper than an unstarted one; it is more expensive, because someone must first work out what the previous attempt actually did. The forecast prices it at zero.

This is the same shape as the retro points figure this run had to correct three times: a status changed in one place and a derived claim left standing in another, with every reader downstream trusting the stale half.

## Steps to Reproduce

1. Open BG0372: Status is Open, the revision history records the reopen, and `Verification depth` still reads `functional (tests red-first)`.
2. Put BG0372 in a worklist and run `sprint plan` - it appears under `excluded from the build forecast (BUILT-NOT-CLOSED, close them)`.
3. Compare the worklist's point total against the forecast's: the reopened units contribute nothing.

## Proposed Fix

1. **A reopen retracts the evidence with the status.** Moving a unit out of a terminal status clears `Verification depth` - or rewrites it to a stated retraction naming the reopen - so no reader can find an unretracted claim on a unit whose delivery was withdrawn.
2. **The planner does not infer BUILT from a field alone.** A unit at Open is not built, whatever evidence field survives on it; the BUILT-NOT-CLOSED exclusion applies only to units actually at a built-but-unclosed status.
3. **The exclusion is loud when it moves the total.** The plan already names the excluded ids; it should also state the points they remove, so a forecast that differs from the batch total explains itself in the same line.
4. A test reopens a unit carrying a verification depth and asserts both that the claim does not survive and that the planner prices the unit at its full points.

## Acceptance Criteria

- [ ] Moving a unit out of a terminal status clears or explicitly retracts its verification-depth claim, so no reopened unit carries an unretracted one.
- [ ] The planner treats a unit at a non-terminal status as unbuilt regardless of any surviving evidence field, so a reopened unit is forecast at its full points.
- [ ] The plan states the points removed by any build-forecast exclusion, so a forecast below the batch total explains the difference in the same line.
- [ ] A test reopens a unit carrying a verification depth and asserts both the retraction and the restored forecast; BG0372, BG0359 and BG0402 are corrected on disk.

## Impact

Reopening is the mechanism this project uses to withdraw a false completion claim, and it is the mechanism that most needs to leave nothing behind. Leaving the verification depth in place means the artefact simultaneously records 'this delivered nothing' and 'this was verified functionally' - and a tool reading the second one prices the sprint wrong.

Here the effect is a forecast 5% low on a sprint whose whole goal is that its own measurements can be trusted. In a consuming project the same field is what a reviewer reads to decide whether a fix was evidenced at all.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-29 | sdlc-studio | Filed |
