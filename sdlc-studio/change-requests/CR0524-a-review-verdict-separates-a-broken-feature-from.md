# CR-0524: a review verdict separates a broken feature from evidence that cannot fail

> **Status:** Proposed
> **Created:** 2026-08-02
> **Created-by:** sdlc-studio new
> **Provenance:** human
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/critic.py, .claude/skills/sdlc-studio/reference-doctrine.md, .claude/skills/sdlc-studio/personas/seats
> **Priority:** High
> **Type:** Improvement
> **Size:** M

## Summary

RUN-01KYZKY5's five independent passes returned 27 REJECT over 38 units, and the operator's reaction was that the reviews read as too critical. Splitting them says otherwise, and says something more useful: roughly 13 were a broken or unreachable feature, and roughly 14 were a CORRECT feature whose verifier cannot fail.

The reviewers knew the difference and said so in prose - 'the implementation is correct, the code is right, the evidence is not' (US0608); 'works through the front door, the defect is the oracle not the feature' (US0615); 'AC1/AC2 themselves are strong, four mutants all KILLED' (BG0401). The verdict vocabulary could not carry it, so both came back REJECT and the summary read as a batch that was half broken.

The two are not the same fact and do not want the same response. A unit whose feature is unreachable is not deliverable. A unit whose feature works and whose test cannot fail IS deliverable and carries a debt - and that debt belongs against the CRITERION, not as a condemnation of the unit.

## Impact

The count is what a reader acts on, and today it flattens 'this does not work' into the same number as 'this works and I cannot prove it stays working'. That misprices the batch in both directions: it reads as catastrophe to an operator, and it gives the author no signal about which repairs are urgent. It also hides the one pattern worth acting on - that a whole run's rejections concentrated in a single defect class.

## Acceptance Criteria

- [ ] A verdict distinguishes a unit that does not work from one that works with evidence that cannot fail, and the second is not spelled REJECT
- [ ] Evidence debt is recorded against the CRITERION it attaches to, naming the mutant that survives, so a repair has a target rather than a whole unit to re-argue
- [ ] The batch summary reports the two counts separately, so a reader can see at a glance whether a run was broken or under-evidenced
- [ ] A unit carrying evidence debt is still refused a terminal status until the debt is cleared or explicitly deferred with a reason - the distinction changes the REPORT, never the bar
- [ ] The seat briefs tell a reviewer which verdict fits which finding, with the RUN-01KYZKY5 examples as the calibration, so the split is applied consistently rather than by each reviewer's taste

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-02 | sdlc-studio | Created via `new` (deterministic) |
