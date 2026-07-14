# CR-0262: The forecast seed is inert: max_cognitive predicts neither cost nor work (r = 0.00). Change the axis, not the coefficient

> **Status:** Proposed
> **Priority:** P1
> **Type:** Improvement
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/route.py, .claude/skills/sdlc-studio/scripts/complexity.py
> **Date:** 2026-07-14
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1

## Summary

Measured across 16 units with real telemetry, the seed the token forecast is computed from - `max_cognitive`, the blast-radius cognitive complexity of the files a unit touches - correlates with actual token cost at r = -0.006 and with actual work done (tool-uses) at r = -0.001. It is not weakly predictive. It carries no signal at all, and no coefficient can rescue it: you cannot scale zero. Every recalibration of `TOKENS_PER_COGNITIVE` (5,000, then 600) was fitting a slope through noise, which is why the model over-forecast by 3.3x and then under-forecast by 0.55x and 0.39x on consecutive sprints. The reason is structural: `max_cognitive` measures how complicated the FILE is, not how much of it must change. A one-line fix in a 2,000-line module inherits the whole module complexity, and a docs unit has none at all - CR0252 seeded at 0, forecast 80,000, cost 205,534.

WHAT THE DATA DOES SUPPORT. Cost tracks work done almost exactly, and the rate is STABLE: roughly 2,300 tokens per tool-use, flat across three sprints (2,868 / 2,294 / 2,302), r = 0.967. So the whole forecasting problem reduces to one question - how many actions will this unit take? The only plan-time signals with any purchase on that are `files_affected` (r = 0.48) and the declared human Effort (r = 0.47). They are roughly equal, both moderate: a persons S/M/L guess is as good as anything the code currently computes, and both are far better than the seed in use.

THIS ALSO CORRECTS A LESSON. RETRO0025 recorded that the estimator was chasing a standard that moved - that the briefs got harder and the work per unit grew with them. The data refutes it: tokens PER ACTION stayed flat, so nothing about the cost model moved. What rose was the NUMBER of actions, which is a property of the units. The inert-seed explanation accounts for all of it, and the moving-standard story was a plausible narrative fitted to a real pattern.

## Impact

Every sprint plan, and the model router. sprint.py forecasts from the inert seed, and route.py difficulty is dominated by the same signal (which is why it scores a docs unit trivial with high confidence - BG0139). Fixing the axis fixes both. It also decides RFC0035: a sprint report can only price work honestly if the cost model underneath it is not noise.

**Effort:** M

## Acceptance Criteria

- [ ] The forecast is computed from a signal with demonstrated predictive power against measured actuals, not from `max_cognitive.` `files_affected` and the declared Effort are the two candidates the data supports; whichever is chosen, its correlation against actuals is stated in the code beside the constant.
- [ ] Any predictor is validated OUT-OF-SAMPLE against measured actuals before it ships, and the validation is recorded. A predictor nobody has tested against outcomes is a guess wearing a number.
- [ ] If no plan-time predictor clears a stated bar, the per-unit forecast is DROPPED rather than kept as decoration, and the plan carries the batch history instead - two five-unit sprints cost 642k and 902k is a defensible basis for planning a third; a per-unit number that has never once been right is not.
- [ ] route.py stops treating a resolved-but-inapplicable code signal as a real zero, so a non-code unit cannot score trivial with high confidence.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-14 | sdlc-studio | Raised |
