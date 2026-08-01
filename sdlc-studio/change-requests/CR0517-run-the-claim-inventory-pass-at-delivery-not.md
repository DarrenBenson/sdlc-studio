# CR-0517: Run the claim-inventory pass at delivery, not at review: every blocking finding of the corrected review loop was prose disagreeing with code in the same diff

> **Status:** In Progress
> **Decomposed-into:** EP0195
> **Created:** 2026-08-01
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/gate.py, .claude/skills/sdlc-studio/scripts/critic.py, .githooks/pre-commit
> **Priority:** High
> **Type:** Feature
> **Size:** M

## Summary

**Relationship to CR0393 (Complete).** CR0393 introduced this pass and put it FIRST in the closing review, which is why the shipped `critic.py brief` carries it and why the three findings below were caught at all. This CR does not duplicate it: it moves the same question from review time to delivery time. CR0393 established that the pass finds the defects; RUN-01KYX375 measured what it costs to ask only at review - three adversarial rounds to find three stale sentences the author could have seen in seconds.

The claim-inventory pass - enumerate every assertion a diff's prose makes and mark each TRUE, FALSE or UNVERIFIABLE against the code - is the highest-yield check this project has, and it runs only at review time, which is the most expensive place to run it.

Measured. Three units of RUN-01KYX375 were re-reviewed from `critic.py brief`, which carries the pass. Each returned exactly one blocking finding, and ALL THREE were prose disagreeing with code in the same diff - not broken code. The seats said so in terms: 'the mechanism itself is sound', 'the delivered code repair is sound and mutation-proof', 'the repair fixes the sign-off half'. What failed was the record.

  BG0413 - `changelog.d` states the collapse signal exits 2; the code returns 3, changed by the author two commits earlier. The stale claim also sat in the docstring of the very test pinning `rc == 3`.
  BG0460 - two acceptance criteria ticked `[x]` which `git diff` disproves (the story they name is byte-identical to the base ref), and a changelog describing behaviour a later round reverted.
  BG0455 - a docstring and an operator-facing message claiming a unit is 'finished bar a signature' while the code checked one of the two halves of that bar.

Every one is decidable from the diff alone, in seconds, by the author. None needs a reviewer, a worktree, or a mutation run. They surfaced at review because nothing asks the question earlier.

## Impact

This is the actual cost driver behind 'the reviews always fail'. The reviews are not too strict and the code is not weak - the record drifts from the code inside a single unit's delivery, and the only thing that notices is a full adversarial pass. Three review rounds were spent finding three stale sentences.

It also feeds the panel sign-off in CR0514: a claim inventory run at delivery means the panel is judging a unit whose prose has already been reconciled with its diff, so the loop converges in fewer rounds and the reviews cost less wall-clock - the operator's stated complaint.

And `changelog.d` fragments assemble into `CHANGELOG.md` at release, so a stale claim there does not stay internal: it ships as the contract, and a consumer wiring behaviour off it inherits the defect a review already rejected once.

## Acceptance Criteria

- [ ] A staged diff that changes a numeric or symbolic literal while its own prose in the same diff still states the old value is flagged, naming both sites - proven against BG0413's exit 2/3 pair
- [ ] A criterion ticked `[x]` in a diff whose named surface that diff does not touch is flagged - proven against BG0460's two ticks over a byte-identical story
- [ ] A diff whose prose and code agree produces NO finding, so the lane cannot be satisfied by one that always fires
- [ ] The lane reports and does not block on first ship, and its yield over one sprint is recorded before any decision to make it blocking
- [ ] Replayed over the RUN-01KYX375 diffs, the lane names the three findings the review rounds cost three passes to find

## Proposed Fix

1. RUN THE PASS AT DELIVERY. A lane over the staged diff enumerates the assertions its prose makes - changelog fragment, docstrings, comments, acceptance criteria, artefact Resolution - and flags each the diff contradicts. It runs where the fix is free, not where it costs a review round.
2. THE CHEAP HIGH-YIELD SUBSET FIRST, since a full natural-language claim check is not mechanisable: a changed literal, exit code, threshold, flag name or constant whose value appears in the same diff's prose with a DIFFERENT value is a machine-decidable contradiction and covers all three findings above.
3. TICKS AGAINST THE TREE. A criterion ticked `[x]` in the staged diff whose named surface is unchanged in that diff is flagged. This is CR0513's checklist item moved to the point of delivery, where it can still be answered honestly.
4. ADVISORY FIRST, THEN RATCHET. Ship reporting, measure the yield over a sprint, and only then decide whether it blocks - a new blocking lane on a gate already at ~450s against a 380s ceiling must earn its place on evidence.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-01 | sdlc-studio | Created via `new` (deterministic) |
