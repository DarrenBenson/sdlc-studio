# CR-0531: a charter's scope query cannot express a decomposition, so the only queued charter's two scope fields disagree

> **Status:** In Progress
> **Decomposed-into:** EP0231
> **Priority:** Medium
> **Type:** Improvement
> **Size:** M
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py, .claude/skills/sdlc-studio/help/sprint.md
> **Date:** 2026-08-04
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

D0127 chose the status-query selector for a charter's `Scope query` and deferred a structured one `to be filed when a charter actually needs it`. The trigger has fired on the only charter in the queue.

SC0001's prose rule reads `CR0507 and CR0510 once refined, plus any close-cost unit they decompose into`. Its query is `--crs Proposed`, which resolves to 15 CRs today - CR0496, CR0497, CR0499, CR0503, CR0504, CR0507, CR0508, CR0509, CR0510, CR0511, CR0523, CR0524, CR0528, CR0529, CR0530 - against an appetite of 8 units. Running `sprint next` on the head of the queue would materialise a batch of 15, mostly units the prose does not name.

The two fields are both honest and they disagree, because the vocabulary cannot say what the rule means. Found by the independent batch review of RUN-01KZ5YXM.

## Impact

A charter whose two scope fields disagree is worse than one with only prose: the prose states the intent, the query is what actually runs, and nothing reconciles them. An operator reading the rule and running the command gets a different batch from the one they authorised.

## Acceptance Criteria

- [ ] A charter's scope query can select the units a request was decomposed into, so a rule like `everything CR0507 decomposes into` is expressible rather than approximated by a status sweep.
- [ ] The vocabulary stays `sprint plan`'s own - one selector grammar in the tool, parsed by the same code - which is the reason D0127 chose the status query and is not given up to gain expressiveness.
- [ ] SC0001's query and its prose rule agree after the change, and a test pins that the queued charter resolves the units its rule names rather than 15 CRs against an 8-unit appetite.
- [ ] A charter whose query cannot be reconciled with its rule is REPORTED at materialise time rather than resolving quietly - the failure this bug is about is two honest fields disagreeing with nothing to notice it.

## Recommendation

Extend the scope query with the selectors the rule needs and no more - at minimum `--parent CRxxxx` (the units a request decomposed into) and `--epic EPxxxx` (already parsed). Keep it inside `sprint plan`'s vocabulary so there remains ONE selector grammar, which is the whole reason D0127 chose the status query. A charter whose query and rule cannot be reconciled should say so rather than resolve quietly - the caveat now on SC0001 is a stopgap, not the fix.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-04 | sdlc-studio | Raised |
