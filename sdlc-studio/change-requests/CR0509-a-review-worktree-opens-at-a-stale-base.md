# CR-0509: A review worktree opens at a stale base, so every delegated reviewer's first act is discovering the units under review do not exist yet

> **Status:** In Progress
> **Decomposed-into:** EP0225
> **Priority:** High
> **Type:** Improvement
> **Size:** S
> **Affects:** .claude/skills/sdlc-studio/scripts/critic.py, .claude/skills/sdlc-studio/reference-review.md, .claude/skills/sdlc-studio/scripts/tests/test_critic.py
> **Evidence:** All seven reviewers dispatched for RUN-01KYTKA1's batch-boundary review hit this, independently, as their first action.
> **Date:** 2026-07-31
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5; human; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

Every one of the seven independent reviewers dispatched for this batch opened in a worktree checked out at a base between five and thirty commits behind the tip. In each case the units under review did not exist in that tree, `critic.py brief` refused them as unknown ids, and the reviewer's first act was to diagnose the staleness and fast-forward before any reviewing could start.

Seven for seven is not a coincidence to be worked around individually. It is also the most dangerous possible failure mode for this ceremony: a reviewer who did NOT notice would have reviewed an older tree and returned a verdict about code that is not the code under review - and the verdict would look exactly like a real one. The seven that caught it caught it only because the brief refused an id, which is luck rather than design.

## Impact

Every delegated review pays a diagnosis-and-recovery tax before it starts, and a reviewer who misses it silently reviews the wrong tree. Verdicts are the evidence half of the two-role gate, so a verdict against a stale base is a gate reporting green over something it did not check - the exact class this repo's current sprint exists to close.

## Acceptance Criteria

- [ ] critic.py brief REFUSES when the working tree does not contain the unit under review, naming the base it found and what it needed, so a reviewer cannot begin against a tree the unit does not exist in
- [ ] A returned verdict records the base commit the review was measured against, so a verdict against a stale tree is visible in the record rather than indistinguishable from a current one
- [ ] reference-review.md states the base contract for a delegated review, so the requirement is in the shipped doctrine and not only in the tool

## Recommendation

Both. The refusal is cheap and closes the seven-for-seven case outright. The reported base is what makes a verdict self-describing: a review that does not say what it reviewed cannot be re-checked later, and this batch produced twenty-six verdicts that a future reader will want to trust.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-31 | Claude Opus 5 | Raised |
