# CR-0262: The forecast seed is inert: max_cognitive predicts neither cost nor work (r = 0.00). Change the axis, not the coefficient

> **Status:** Complete
> **Priority:** P1
> **Type:** Improvement
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/route.py, .claude/skills/sdlc-studio/scripts/complexity.py
> **Verification depth:** functional - the two contaminants were reproduced independently before the result was accepted. files_affected runs +0.72, -0.34, +0.87 WITHIN the three sprints (pooled +0.45): it flips sign, so it is not a predictor. 'Was Effort declared at all?' scores r = +0.425 against cost - a calendar artefact, since the field only exists on later, larger units - so the honest Effort value correlation is 0.353, not the 0.47 previously quoted. The plan now leads with batch history and carries no per-unit token_budget; route.py reports CR0252 as 34/low/LOW confidence with code and risk MISSING (was 14/trivial/HIGH), while a code unit (BG0133, 60/high) is unchanged.
> **Depends on:** BG0140
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

## Design direction (operator decision, 2026-07-14, with the literature)

**Decision: swap the axis, KEEP the per-unit number - but build it on three factors, and lead with
velocity.**

### The concept was right; the object was wrong

The operator's phrase settles the diagnosis: **"complexity of the code being worked on."** We measure
the complexity of the FILE. That is the complexity of the CHANGE. A one-line fix in a 2,000-line module
scores maximum `max_cognitive` and does nothing, which is exactly why r = 0.00. Complexity is not a dead
axis - it was read through the wrong lens. Measure the delta, not the container.

### The three factors, from established practice

Standard story-point practice sizes work on THREE dimensions, and this estimator has one:

| factor | what it is | what we have today |
| --- | --- | --- |
| **Volume** - amount of work | size of change; **test impact** (tests written or rewritten) | nothing |
| **Complexity** - how intricate | complexity OF THE CHANGE | `max_cognitive` of the FILE (r = 0.00) |
| **Risk / uncertainty** | **clarity of the requirement**; novelty; dependencies | a `novel` subscore, barely weighted, never validated |

The operator's independent list - "size of change and test impact and clarity of requirement, a good
requirement making little functional change needing fewer tests rewritten" - reconstructs this model
from thirty years of practice. **Test impact is the sharpest signal on offer and we capture none of it:
it measures WORK rather than CODE, and it is mechanically derivable from the test files that cover the
affected paths.** Requirement clarity is likewise derivable in this repo - AC count, AC specificity,
whether the unit has executable verifiers.

### What the evidence says about the ceiling, and it is sobering

The empirical literature is blunt: the correlation between human-expert story points and actual
development effort is **medium or low in 93% of projects studied**, and estimator consistency
**collapses above 5 points** - people cannot reliably size anything more than about five times a
reference unit.

So our measured r = 0.47 for the human `Effort` guess is **not a defect in this tooling. It is roughly
the industry ceiling.** Nobody predicts per-unit effort well. What working teams actually rely on is
RELATIVE sizing plus MEASURED VELOCITY - which is precisely what our own data shows: the batch rate
(~2,300 tokens per tool-use) is stable across three sprints while every per-unit forecast fails.

### Therefore

1. **Rebuild the seed on the three factors** - change-size + test-impact (volume), change-complexity
   (not file-complexity), AC/requirement clarity (uncertainty). Validate out-of-sample before shipping.
2. **Lead with velocity, not the estimate.** The per-unit number stays (operator's call, and it is
   better than zero), but the BATCH HISTORY is the headline, because it is the only thing the
   measurement supports. Do not let a per-unit number that is right half the time set the tone of a
   plan.
3. **State the correlation next to the number.** A forecast whose r is unknown is the thing this whole
   CR exists to abolish; a forecast whose r is PUBLISHED can be judged by the operator reading it.
4. **Sizing beyond ~5 points is a PLANNING failure, not an estimation failure.** If humans cannot size
   big units, stop asking them to - break the unit down. The breakdown machinery already exists.

Sources: Atlassian and Mountain Goat Software on the three factors of story-point estimation; Tawosi
et al., "On the Relationship Between Story Points and Development Effort in Agile Open-Source Software"
(ESEM 2022) for the 93% finding and the above-5-points consistency collapse.

## Correction to the section above (same day, operator challenge)

**The "industry ceiling" framing was wrong, and it is an instance of LL0030 committed one turn after
LL0030 was written.**

The study finds the correlation is medium-or-low in 93% of PROJECTS. That is a fact about what
estimation TYPICALLY IS. It was written up above as a CEILING - a claim about what estimation CAN BE -
and those are different statements. A population average hides its variance, and "most are poor at
this" has never implied "nobody can be good at it".

The operator's causal point is sharper than the study's: **an engineer does not want to estimate, they
want to write code.** A study of story points in the wild therefore measures, to an unknown degree, HOW
MUCH PEOPLE CARE rather than how well they could do it if they did. Low engagement and low capability
produce an identical correlation, and the study cannot distinguish them. Accepting 0.47 as a bound was
fatalism dressed as evidence.

**And it does not need assuming, because this loop can now MEASURE it - per estimator.**

The forecast, the actual and (CR0261) the model are all recorded. Record WHO estimated a unit and the
tool can report: "your S/M/L calls run at r = 0.61, the auto-estimate at 0.30 - trust yours", and name
the kinds of unit an individual systematically under-calls. Feedback on your own past calls is the one
intervention known to improve human estimation, and it is nearly free here.

**The hazard this exposes in what shipped TODAY.** BG0136 made `Effort` MANDATORY at filing. If
estimating is a chore an engineer resents, a mandatory estimate produces a CARELESS estimate - and a
careless estimate is worse than no estimate, because it looks like data and gets averaged into a
forecast. The grooming gate may be manufacturing exactly the noise it was built to eliminate.

That is testable, not arguable: compare the accuracy of `Effort` values recorded BEFORE the gate made
them compulsory against those recorded after. If mandatory estimates are measurably worse, the gate
needs a different answer - a required "I do not know" is an honest input; a coerced "M" is not.

### Revised direction

- Rebuild the seed on the three factors (volume incl. TEST IMPACT, complexity OF THE CHANGE, requirement
  clarity), as above. Unchanged.
- **Publish the correlation of every predictor, including the human one, and per estimator.** Do not
  assume the human is weak; measure whether they are. An estimator that reports its own accuracy is the
  only kind that can earn trust or lose it honestly.
- **Watch for coerced estimates.** Test whether mandatory `Effort` is less accurate than voluntary
  `Effort`, and give "unknown" a first-class value so nobody has to invent a size to get past a gate.

## Absorbs BG0139 (2026-07-14)

BG0139 (the model router scores a docs unit trivial with HIGH confidence) is closed as a duplicate of
this CR. Its three fixes are AC4, AC1 and AC2 here, verbatim. Same root cause: the router and the
forecast are dominated by the same inert signal, so one fix serves both consumers. **Do not enable
`routing.enabled` until this ships and the seed is validated out-of-sample.**
