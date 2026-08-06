# BG0531: a hand-applied mutant is registered with no assertion that its anchor was unique, so a mutation run can report a false SURVIVED for a function it never edited

> **Status:** Open
> **Severity:** Medium
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/mutation.py, .claude/skills/sdlc-studio/scripts/tests/test_mutation.py
> **Evidence:** Stated as a narrowing on US0632's AC3 at delivery, 2026-08-06, RUN-01KZBBZ0, rather than left as an unmet criterion. The two lies it names both occurred during this session's own review rounds: a non-unique anchor patched the wrong function and reported a false SURVIVED, and a same-length mutant reused a cached .pyc.
> **Created:** 2026-08-06
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

`mutation.py register` records a mutant applied by hand. It takes the target, the mutant's prose, the test and the verdict, and asserts nothing about how the edit was made. The automated engine has no equivalent hazard - it selects by AST node, so there is no anchor to be ambiguous - but the registered path is exactly where a human or an agent does a string replacement, and that is where the two known lies live: a same-length replacement inheriting a cached module, and an anchor string occurring more than once so the edit lands in a different function from the one the criterion names. The first is already closed for registered mutants only by luck, because the operator happens to run the suite themselves. The second is not closed at all.

US0632 delivers the plan-execution join and states this limb as NOT delivered rather than claiming it, because the engine it was written against has no anchor to assert. The hazard is real and was observed twice in one session: a substring anchor patched the wrong function and reported a false SURVIVED, and a same-length mutant reused a cached `.pyc` and did the same.

## Steps to Reproduce

1. Apply a mutant by hand using a string replacement whose anchor occurs twice in the target file. 2. The wrong occurrence is edited; the criterion's own function is untouched. 3. Its test passes, because the code it pins was never changed. 4. `mutation.py register --verdict survived` records a survivor against a criterion whose test is in fact sound, or `--verdict killed` records a kill that measured a different function. Nothing in the tool objects, because nothing in the tool saw the edit.

## Proposed Fix

Give `register` an optional `--anchor` and, when supplied, refuse unless the target contains it exactly once - and record the count in the ledger entry either way, so a registration made without one is visibly weaker evidence rather than indistinguishable. That keeps the practice the verb exists for (apply, watch it go red, restore) while making the one property that cannot be checked afterwards checkable at the moment it is claimed.

The same entry should record whether bytecode was purged, on the same reasoning: `register` is a self-report, and a self-report that cannot state its own soundness is a claim the ledger presents beside measurements.

## Acceptance Criteria

- [ ] The behaviour described is corrected: `mutation.py register` records a mutant applied by hand.
- [ ] The proposed fix lands, pinned by a test: Give `register` an optional `--anchor` and, when supplied, refuse unless the target contains it exactly once - and record the count in the ledger entry either...

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-06 | sdlc-studio | Filed |
