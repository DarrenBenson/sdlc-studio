# CR-0500: The adversarial review runs at the close, so every defect it finds becomes close work - it belongs at the delivery cadence

> **Status:** Complete
> **Decomposed-into:** EP0190
> **Priority:** High
> **Type:** Improvement
> **Size:** M
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/critic.py, .claude/skills/sdlc-studio/reference-reconcile.md, .claude/skills/sdlc-studio/templates/core/definition-of-done.md, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_critic.py
> **Evidence:** RUN-01KYNKDP measured: delivery 00:30-05:40 (~5h), close 05:40-12:15 (6h35m). Three of the seven close commits are fixes (06c806d7 nine stop-ships, 69048d58 BG0402 plus eight restored test classes, 6efcb8d4 four round-2 bugs). Gate and suite time across the whole close is about 70 minutes - roughly 18%. The rest is repair work the close-time review generated.
> **Date:** 2026-07-29
> **Created-by:** sdlc-studio file
> **Raised-by:** RUN-01KYNKDP close, measured; human; v1

## Summary

The close cost more than the sprint it certified, and the tests are not why.

RUN-01KYNKDP delivered in about five hours and took six and a half to close. Measured, the gate and suite runs across the entire close come to roughly 70 minutes - about 18% of it. The other 82% is repair: nine stop-ship fixes, eight test classes restored after a bad revert, then four more bugs found by re-reviewing those fixes.

Every one of those was a real defect, and none was visible to 5,163 passing tests: a false green written by the mechanism built to refuse false greens, a release guard that reported 'no close is owed' when it could not read the tree, and eight guard classes silently deleted (the suite reported 510 passing, because deleted tests do not fail). So the review earns its cost. The problem is WHERE it sits.

The adversarial review runs at the close. That single placement decision means every finding it makes is, by definition, close work - it arrives after the sprint is nominally over. A human sprint that spent two weeks delivering and two weeks closing would not survive the quarter, and the shape here is identical: QA is happening after sign-off rather than inside the sprint.

The cadence already exists to fix it. This project commits in batches of at least 20 points; that batch boundary is the natural review point. Reviewed there, a finding is delivery work in the batch that caused it, priced against that batch, and fixed by a context still holding it. The close then certifies work that has already been reviewed, which is what a close is for.

A second, compounding effect the run demonstrated: a review of the REPAIRS then found nine more mutants surviving, because the repairs were written fast, late, and self-reviewed. Repairs made under close pressure are the least-reviewed code in the sprint and sit in the most load-bearing paths. Batch-cadence review removes that pressure entirely.

## Impact

The close is the ceremony most likely to be skipped under pressure, and the surest way to guarantee it gets skipped is to make it cost more than the delivery. RUN-01KYNKDP is that case measured: 5 hours to deliver, 6h35m to close, with the excess being repair work rather than ceremony.

The damage is not only time. Repairs written at close time are authored fast, late, and self-reviewed, then land in guards and release paths - the highest-consequence code in the project. This run shipped a fail-open release guard, an orphaned process group and eight deleted test classes in exactly that window, all green.

This is inherited by every consuming project. The shipped lifecycle puts the review at the close, so any team adopting it takes on the same unbounded tail and the same incentive to stop closing at all.

## Acceptance Criteria

- [ ] A delivery batch reaching the project's commit threshold has a defined review point, and the review's surface is that batch rather than the whole sprint.
- [ ] A finding from a batch review is filed as a delivery unit against that batch, so its cost is priced where the work was rather than as close overhead.
- [ ] `sprint close` REFUSES a batch containing units no independent review has covered, and names them - the close asserts coverage rather than performing the review.
- [ ] A repair written in response to a finding is itself covered by a later batch review, never shipped self-reviewed.
- [ ] The run record carries close elapsed against delivery elapsed, so a close costing more than its sprint is visible rather than felt.
- [ ] The shipped definition-of-done and lifecycle documentation place the review at the batch boundary, so a consuming project inherits the corrected cadence rather than this one.

## Steps to Reproduce

1. `git log --format='%h %ad %s' --date=format:'%H:%M'` over RUN-01KYNKDP: delivery commits end 05:40, the close's last fix lands 12:15.
2. Count the close commits that are fixes rather than records: three of seven.
3. Sum the gate and suite time across the close: about 70 minutes against a 6h35m elapsed.
4. Read the run record: the review that produced that work ran once, after `sprint close`.

## Proposed Fix

Move the adversarial review to the batch boundary, and make the close assert that it happened rather than perform it.

1. **A review point per delivery batch.** When a batch reaches the commit threshold the project already uses, an independent context reviews THAT batch - a bounded surface, reviewed by someone not holding the author's context, while the work is fresh.

2. **Findings are delivery units in that batch.** Filed against the batch that caused them and fixed before the next batch opens, so the cost lands where the work did and shows up in that batch's points rather than as unpriced close overhead.

3. **The close ASSERTS coverage, it does not perform the review.** `sprint close` should refuse a batch carrying units no independent review has covered, and say which. Today it runs the review, which is what makes the close unbounded.

4. **Repairs are reviewed like any other change.** A fix written in response to a finding is the least-reviewed code in a sprint and usually sits in a guard. It joins the next batch's review rather than shipping self-reviewed - this run's re-review of nine repairs found nine surviving mutants and four new defects, which is the whole argument.

5. **Measure it.** Record close elapsed against delivery elapsed on the run record. A close that costs more than the sprint is a signal, and nothing currently computes it.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-29 | RUN-01KYNKDP close, measured | Raised |
