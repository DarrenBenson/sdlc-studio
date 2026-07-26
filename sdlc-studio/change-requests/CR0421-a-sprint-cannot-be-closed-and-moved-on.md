# CR-0421: a sprint cannot be closed and moved on from: the batch is immutable, and the close chases a moving target it diagnoses but cannot exit

> **Status:** Complete
> **Decomposed-into:** EP0162
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

## Addendum: the close was eventually forced through, and how confirms the diagnosis

This CR was raised mid-close. The close then completed - **on the ninth attempt** - and every step
needed to get there is one of the failure modes above, so the evidence is no longer predictive.

**1. The grandfathering pressure is real, not hypothetical.** The CR warned that with no legitimate
exit the available moves are to force a false Done or to bump `conformance.adopt_after`. The bump is
what happened: 136 -> 179, to grandfather **one** unit, US0179 - a different author's story, in a
different epic, **not in the batch**, missing `verified` (all its ACs are manual) and `promoted`
(planning-tier scaffold). Nothing about it was this sprint's correctness. It blocked this close only
because the conformance lane judges the whole workspace when the tree is clean.

The operator's exposure here is worth stating plainly: the honest thing was done - US0179's substance
was independently re-verified first, and the backup measured 29,600 files / 453,602,723,182 bytes,
exactly its claim, checked after the source drive had been wiped - but *the tool did not require
that*. A bump satisfies the lane whether or not anyone looks. **The gate rewarded the cheap move and
was indifferent to the honest one.**

**2. Dropping a unit required hand-editing `run-state.json`.** With no `sprint.py batch --drop`, and
with `Deferred` failing to release the done-gate, the only route was to edit the run's tool-owned
state by hand and append a `batch_changes` record for auditability. That is a consuming project
writing to the framework's own state file because the framework offers no verb for a routine sprint
event. AC1 of this CR is exactly that verb.

**3. A satisfied lane can still read red - the anchor-commit-time trap.** `_review_current` compares
`reviews/LATEST.md`'s **commit** time against each artefact's. Re-running the review and re-stamping
via `review_prep.py close` wrote **byte-identical** anchor content, so git saw no change, the file
kept its older commit time, and the lane stayed red over a review that had genuinely just been
re-run. The remedy the lane prints - *"run `review` before closing"* - is the thing that had just
been done, and repeating it cannot help.

It only cleared once the anchor was given a *substantive* edit. Two consequences worth fixing:

- the lane should compare against the review **record** (`review-state.json`, which
  `check_review_currency.py` already reads correctly) rather than inferring currency from a file's
  commit time - the same class as the BG0124 finding in the consuming project;
- and while it disagrees with the project's own currency checker, the two give **opposite verdicts on
  identical state**. During this close, `check_review_currency.py --report` said *0 of 4 legs stale*
  while the close's `review-current` lane said stale on three artefacts.

**4. The attempt counter is the honest metric.** `close_attempts` reached 8 before success, and the
close's own narration moved `outstanding set 3 -> 4 (growing - chasing a moving target)` and back
again as lanes re-broke each other. A close that needs nine attempts, a hand-edited state file and a
grandfather bump has not been completed so much as survived.

### One extra AC this addendum adds

- [ ] a lane must not be satisfiable only by a *substantive* edit to an artefact whose content is
      already correct - currency is a property of the review RECORD, not of a file's commit time

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-26 | sdlc-studio | Raised |
| 2026-07-26 | agent | Addendum: the close completed on attempt 9 - the grandfather bump, the hand-edited run-state, and the anchor-commit-time trap all confirm the diagnosis |
