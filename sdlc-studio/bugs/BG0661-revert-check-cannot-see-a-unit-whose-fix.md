# BG0661: revert-check cannot see a unit whose fix and evidence share one file - it reverts the tests with the change and reports green

> **Status:** Open
> **Severity:** Medium
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/gate.py, .claude/skills/sdlc-studio/scripts/tests/test_gate.py
> **Evidence:** Boundary run 2026-09-10 on commit 24401fea: revert-check 15.7s, 10 unit(s) examined, none stayed green without its change. Hand check the same morning: reverting the sweep comparisons in DryRunScratchParityTests leaves 11 of 11 green. Two independent review seats reached the same finding on BG0601.
> **Created:** 2026-09-10
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5; human; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

The revert-check lane reverts each batch unit's declared production files to the run's base ref and re-runs that unit's own Verify selectors, on the rule that a test passing without its change never reached it. For a unit whose Affects names a TEST file - because the fix itself is in a test, which this corpus has several of - the revert takes the tests away along with the change, so the selectors are reverted too and the lane reports nothing. Measured on 2026-09-10: the push boundary reported 10 units examined, none stayed green without its change, and by hand twenty minutes later BG0601 did exactly that - restoring the two-field slices in the sweep left all 11 tests in its own criteria's class green. BG0601's Affects is one test file, so the lane could not have seen it. The lane is ADVISORY, so nothing was gated wrongly, but its recorded yield is overstated by however many test-only units a run carries.

## Steps to Reproduce

1. Take a unit whose Affects names only a test file - BG0601 in RUN-01M20RWX.
2. Run gate.py --boundary push and read the revert-check line: it counts the unit as examined and reports it green.
3. By hand, revert only the production half of that unit's change inside the test file and re-run the unit's Verify selectors. They pass.
4. The lane and the hand check disagree, and the hand check is right.

## Proposed Fix

Report rather than count. A unit whose declared files are all test files cannot be revert-checked by this method, and the lane should say so by id instead of adding it to the examined tally - a number that includes cases the method cannot judge is the same shape of overstatement as a ratchet declared above what it measures. Whether such units can be checked at all is a separate question: reverting the production hunks inside a test file needs a hunk-level revert, which is a design decision rather than a fix, and should be recorded as one before it is attempted.

## Acceptance Criteria

- [ ] **AC1** The behaviour described is corrected: The revert-check lane reverts each batch unit's declared production files to the run's base ref and re-runs that unit's own Verify selectors, on the rule that...

## Impact

The yield figure accumulating in the local revert-check record is the number this lane's promotion from advisory to blocking will be decided on. Counting units the method cannot judge as units it judged and cleared makes that decision on a wrong number.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-10 | Claude Opus 5 | Filed |
| 2026-09-10 | Claude Opus 5 | Ruled OPEN for v5.1 on 2026-09-10, under D0186's disclosure half. revert-check is an ADVISORY lane whose yield is still being measured, so a blind spot in it holds nothing back and misleads nobody: the boundary run records what it examined and this bug names, by id, the class it cannot see - a unit whose production change and its evidence live in one file, which is every test-only unit. Two independent seats reached it on BG0601 and a hand check confirmed 11 of 11 green after the revert. Fixing it means deciding what 'production file' means for a unit that only adds tests, which is a design question and not a patch. |
