# BG0561: a re-plan over an open run resets the appetite to the standing capacity while leaving the resize record standing, so the ledger and the breaker disagree about the ceiling

> **Status:** Fixed
> **Verification depth:** functional (executed: a run state carrying a recorded resize keeps its raised ceiling; mutation: 1 declared mutant KILLED after the FIRST verifier was found vacuous - it asserted a source string the mutant left intact, so it caught nothing; restore byte-exact)
> **Severity:** Medium
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py
> **Evidence:** Hit while planning RUN-01KZM49Y, 2026-08-09. `sprint appetite resize --units 8 --reason ...` reported `appetite resized to 960min/8units (standing: 960min/64units)`. A subsequent `sprint plan --write` over the same open run, to record a content review, reported `appetite 960min/64units` and left run-state at `appetite: {units: 64, ...}` while `appetite_changes` still carried the resize with `to: {units: 8}`. The ledger records a resize that is no longer in force and nothing says so.
> **Created:** 2026-08-09
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

`appetite resize` exists so a run's ceiling can be raised or lowered ON THE RECORD rather than overrun silently. A re-plan over the same open run re-resolves the appetite from the standing capacity and overwrites it, but does not touch `appetite_changes` - so the two halves of the same fact disagree, and the half a reader trusts is the one that is wrong.

The direction of the failure is the bad one. The breaker reads the live appetite, so a resize DOWN is silently discharged and the run may spend past the ceiling somebody deliberately set, while the record continues to assert the lower number. A reader auditing the run afterwards finds a resize entry and no indication it was reverted.

A re-plan over an open run is not an unusual act. It is what the tooling itself invites when a plan-time field was omitted: `sprint plan` prints `content review (plan): UNANSWERED - record it with --content-review`, and the only way to record it is to run `plan` again, which is the operation that resets the appetite.

## Steps to Reproduce

1. Open a run with `sprint plan --worklist <file> --write --sprint-goal "..."`. 2. `sprint appetite resize --units 8 --reason "..."` and read the confirmation. 3. Re-run the same `sprint plan --write` with `--content-review partial --content-missing "..."`. 4. Read `sdlc-studio/.local/run-state.json`: `appetite.units` is back to the standing capacity, and `appetite_changes` still records the resize to 8.

## Acceptance Criteria

- [x] **AC1** Given an open run whose appetite was raised by a recorded `appetite resize`, when a re-plan runs over it, then the resize is PRESERVED - a ceiling moved on the record with a compulsory reason must not be silently re-resolved from the standing capacity.
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py -k a_recorded_resize_survives_a_replan

## Proposed Fix

A re-plan over an ALREADY OPEN run must preserve an explicit resize rather than re-resolving over it - the resize is the more specific statement, and the appetite resolution order already prefers the more specific source. Either carry the recorded resize forward, or refuse the re-plan and say the appetite would be reset. Whichever is chosen, the invariant to pin is that `appetite` and the last entry of `appetite_changes` never disagree, asserted as a property over a resize-then-replan sequence driven through the CLI rather than over either command alone - each is correct in isolation, which is why no existing test sees this.

## Test Plan

| Criterion | Mutant - the production change this test must fail on | Title |
| --- | --- | --- |
| AC1 | in sprint.py, delete the `if prior.get(...appetite_changes...)` preservation branch so a re-plan overwrites a recorded resize | Given an open run whose appetite was raised by a recorded `appetite resize`, when a re-plan runs over it, then the resize is PRESERVED - a ceiling moved on the record with a compulsory reason must not be silently re-resolved from the standing capacity. |

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-09 | sdlc-studio | Filed |
