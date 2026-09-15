# CR-0579: revert-check's set-aside report merges four reasons under one token, repeats error text unbounded, and reads a declared but unedited file as the unit's production

> **Status:** Proposed
> **Priority:** Medium
> **Type:** Improvement
> **Size:** S
> **Affects:** .claude/skills/sdlc-studio/scripts/gate.py, .claude/skills/sdlc-studio/scripts/tests/test_gate.py
> **Evidence:** Independent delivery review, RUN-01M2JA6J 2026-09-15: verdicts/BG0661-delivery-engineering.txt (engineering seat); verdicts/BG0661-delivery-qa.txt (qa seat); verdicts/US0625-delivery-qa.txt (qa seat); verdicts/US0625-delivery-engineering.txt (engineering seat); verdict rows in sdlc-studio/reviews/critic-verdicts.md.
> **Date:** 2026-09-15
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

The (reported) token merges four `verify_ac` reasons - a test-only unit, an unreadable Affects path, an unreadable base blob, and nothing measurable or all exempt - so a reader cannot tell a test-only unit from a broken one (gate.py:1410-1412). The set-aside list is never truncated and repeats each unit's full error text: a base ref that does not resolve gives seven units about 820 characters of the same reason (gate.py:1412, 1425), and a 21-unit batch in a shallow clone gives a line of about 2.5k characters. The crash-with-nothing-examined branch (gate.py:1432, the else absence arm) has no test - a mutant dropping the tokens only there survives all three RevertCheck classes, though the code comment and the changelog claim every path - and the error reason text is unpinned (a bare (error) survives, gate.py:1411). The fixture helper's batch or [...] (`test_gate.py`:7035) quietly turns an explicit batch=[] into the default batch. Separately, the lane reports a doc-and-test unit as never reached because it reverts only a file the unit declares in Affects but never edits, and does not treat the doctrine file the unit did edit as production.

## Impact

Operators reading the push boundary's advisory revert-check output: a broken unit and a test-only one read alike, a shallow clone prints a wall of repeated text, and a doc-and-test unit is reported for a file its diff never touched. The lane is advisory while its yield is measured, and noise of this kind lowers the measured yield.

## Acceptance Criteria

- [ ] A set-aside unit's token names which of the four reasons applies, so a test-only unit reads differently from one whose Affects path is unreadable
- [ ] A reason shared by several units prints once with the units listed, so seven units with one unresolvable base ref print the reason one time
- [ ] A unit whose declared Affects file is unchanged against the base ref is not reported as never reached on that file's account, beside a unit whose edited file is reverted as today

## Recommendation

Give each set-aside reason its own token. Print a reason several units share once, listing the units. Revert only the Affects files the run's diff changed, and count a doctrine or reference file as production when the unit's criteria read it. Pin the crash-with-nothing-examined branch and the error text, and make the fixture helper keep an explicit empty batch.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-15 | sdlc-studio | Raised |
