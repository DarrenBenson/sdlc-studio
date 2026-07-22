# CR-0391: The token forecast has no fixed-cost parameter, and two measured sprints say the fixed cost is roughly 300 times the marginal one

> **Status:** Proposed
> **Priority:** High
> **Type:** Improvement
> **Size:** M
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py,.claude/skills/sdlc-studio/reference-sprint.md
> **Date:** 2026-07-22
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1

## Summary

BG0254 established that the forecast prices only the BUILD. RUN-01KY3MFX supplies the second measured data point and it says something sharper: the missing term is not a bigger rate, it is a FIXED per-sprint cost the model has no parameter for. RUN-01KY321Q delivered 18 points for at least 4,119,916 tokens (at least 228,884 per point). RUN-01KY3MFX delivered 100 points for at least 5,194,538 (at least 51,945 per point). That is 5.5 times the points for 1.26 times the tokens, which is not a rate behaving like a rate. Fitting the two as fixed plus marginal times points gives a marginal of about 13,105 tokens per point and a fixed of about 3,884,023 per sprint. The marginal term is the right ORDER as the shipped 25,000 seed, so the seed was never badly wrong about the build; what the model omits is the ceremony, the review rounds, the repairs and the close, and at these batch sizes that omission is about 300 times larger than the term the model does have. Worth noting the shipped seed's own basis says a base term does worse than no base term, and that was true of the data it was fitted on: runner-era per-unit measurements with no sprint ceremony, no review rounds and no close. The estimator is not wrong about what it measured, it is being applied to a different activity.

## Impact

Every plan and every capacity check. Under-forecasting is worst at SMALL batch sizes, which is the opposite of the usual intuition: an 18-point sprint was out by more than ten times while a 100-point sprint was out by about two, because the fixed cost is amortised. So the model most misleads exactly when a team is being careful and keeping batches small. The capacity breaker reads the same number, so it cannot fire meaningfully either.

## Acceptance Criteria

- [ ] The forecast carries an explicit fixed per-sprint term alongside the per-point term, and the plan shows both rather than a single product.
- [ ] The fixed term is MEASURED from the project's own velocity record where two or more sprints carry a whole-sprint actual, and reads UNMEASURED rather than a default where they do not.
- [ ] The shipped seed's basis text stops claiming a base term does worse, or states the condition under which that was true (runner-era per-unit data with no ceremony).
- [ ] A two-point fit is never applied automatically: the plan states how many sprints the fit rests on, and refuses to publish a fitted fixed term below a stated minimum.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-22 | sdlc-studio | Raised |
