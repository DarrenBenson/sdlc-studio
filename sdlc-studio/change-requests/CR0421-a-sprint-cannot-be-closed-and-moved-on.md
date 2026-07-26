# CR-0421: a sprint cannot be closed and moved on from: the batch is immutable, and the close chases a moving target it diagnoses but cannot exit

> **Status:** Proposed
> **Priority:** High
> **Type:** Improvement
> **Size:** M
> **Affects:** scripts/sprint.py,scripts/gate.py,reference-sprint.md
> **Date:** 2026-07-26
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1

## Summary

Closing one real sprint (RUN-01KY2X68, a 6-unit batch) took 12 preflight blockers down to 2 and then stopped converging. The close diagnosed this itself - `outstanding set 3 -> 4 (growing - the close is chasing a moving target, not converging)` - and offered no way out.

**Three gaps combine.**

**First, the batch is immutable.** There is no `sprint.py` command to DROP a unit or SWAP one in, and real sprints do both constantly. The nearest workaround, transitioning the unit to `Deferred`, does NOT remove it from the done-gate: US0167 was deferred with a recorded reason and the close still reports `US0167 -> Done blocked`. A batch chosen on day one therefore binds the close on day five, and a unit that was never started holds a fully delivered sprint open indefinitely.

**Second, the fail-forward exit refuses exactly when it is needed.** `--file-and-close` is documented as *the bounded exit for a blocked close*, but is REFUSED while any correctness lane is red - and conformance counts as correctness. When the tree is clean the conformance lane has no diff to scope to, so it judges the WHOLE workspace (188 units here), and out-of-batch debt blocks an in-batch close. The last remaining unit was US0179: a different author, a different epic, not in this batch, missing `verified` because all its ACs are manual and `promoted` because it is a planning-tier scaffold. None of that is this sprint's correctness.

**Third, satisfying one lane re-breaks another.** Giving US0161 a machine-checkable AC - it had none, every AC manual, so it could never carry a `Verified:` stamp - immediately made `review-current` stale on the artefact just edited. Fixing that needs another review, which touches more artefacts, which re-stales it.

\*\*Net effect:\*\* an operator who has signed off every unit, judged the goal, written and validated the retro, extracted the lessons and run a fresh review still cannot close - and the only routes left are the ones the tool exists to prevent: forcing a false Done, or bumping `conformance.adopt_after` to grandfather work authored the same day.

## Impact

Anyone running a sprint that does not land exactly as planned, which is most of them. The operator who hit this had delivered 5 of 6 units and signed off all of them.

\*\*What breaks:\*\* the run stays `outcome: running` indefinitely, so the next `sprint plan` either refuses or archives the run the ceremony still needs - this project has already recorded that as L-0045, and recorded it repeating the same day. Velocity, cycle time and the retro cadence all key off closed runs, so an unclosable sprint silently stops the measurement the framework exists to provide.

**Worse, the pressure points the wrong way.** With no legitimate exit, the available moves are to force a Done on undelivered work or to grandfather same-day work past the conformance cutoff. Both are precisely what the gates are for. A ceremony that cannot be completed honestly teaches operators to complete it dishonestly - which costs more than the blocked close ever did.

## Acceptance Criteria

- [ ] a unit can be DROPPED from a batch with a recorded reason, and the done-gate and sign-off lanes stop demanding it
- [ ] a unit can be ADDED to an open batch, and is then held to the same gates as the rest
- [ ] dropping is distinct from Deferred in both vocabulary and effect - Deferred judges the WORK, dropping judges THIS BATCH
- [ ] correctness lanes are scoped to the batch, or --file-and-close can file out-of-batch correctness debt with it named
- [ ] when the outstanding set grows across consecutive close attempts, the close offers the bounded exit rather than only naming the divergence
- [ ] a close never requires an edit that invalidates a lane the close has already passed - stated in reference-sprint.md and covered by a test

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-26 | sdlc-studio | Raised |
