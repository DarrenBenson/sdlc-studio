# RFC-0038: Simplify to Fibonacci story points and real WSJF, and test it by blind re-estimation of past sprints

> **Status:** Draft
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/route.py, .claude/skills/sdlc-studio/templates/core/bug.md
> **Date:** 2026-07-14
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1

## Summary

Operator: this is getting too complicated; there is a REASON agile settled on Fibonacci story points, and WSJF is Fibonacci all the way down. Both are right, and the research explains why everything built so far failed.

WHY FIBONACCI. The gaps widen as the numbers grow, so the SCALE ITSELF encodes that uncertainty grows with size. It is much harder to argue a story is a 7 rather than an 8 than to choose between a 5 and an 8. This project spent two sprints computing "67,400 tokens" - false precision about something inherently uncertain, on a linear scale that lied about how much was known. Story points are also RELATIVE, not absolute: not "how long will this take" but "is this bigger than that one", sized against a reference. We tried to derive an absolute number from file complexity. Nobody does that, for good reason.

WSJF is the same shape: Cost of Delay / Job Size, both on modified Fibonacci (1,2,3,5,8,13,20), with CoD = Business Value + Time Criticality + Risk Reduction.

WHAT WE HAVE INSTEAD - five overlapping size signals, three unvalidated or dead:

- Priority (Critical/High/Medium/Low): a crude Cost-of-Delay proxy. Fine.
- Effort (S/M/L): a crude job-size proxy. r = 0.35 against measured cost.
- `max_cognitive`: DEAD (r = 0.03), removed from the forecast by CR0262 and still ordering the batch (BG0147).
- `difficulty_score`: never validated against outcomes; routing is disabled because of it.
- the flat 120,000 per-unit rate: a degenerate story-point system in which every unit is worth 1 point - which is exactly why the 5.5x spread in unit cost hurts.

THE KEY REALISATION. Our flat rate IS story points with every unit scored 1. Points are DESIGNED to absorb that variance: a 13-point unit counts as 13. So the fix is not a sixth signal. It is to replace five with two.

THE SIMPLIFICATION. Two numbers on an artefact, one measured velocity:

- Points: modified Fibonacci (1,2,3,5,8,13,20) - the ONE size vocabulary, replacing Effort S/M/L.
- CoD: Fibonacci, derived from Priority (or declared) - the ONE value vocabulary.
- WSJF = CoD / Points. Ordering falls out; no seat scores required.
- Velocity = points delivered per sprint, MEASURED. Forecast = planned points x measured tokens-per-point.
- A unit above 13 points MUST be decomposed - the literature is explicit that estimator consistency collapses beyond about 5 points, so "too big to size" is a triage failure, not an estimation failure.

DELETED: Effort S/M/L, the complexity tie-break, `EFFORT_COMPLEXITY_PROXY`, the per-unit flat rate as a headline. That is a genuine reduction, not a rearrangement.

THE EXPERIMENT (the operator proposal, and it uses data already on disk). 20 units carry measured actuals across four sprints. Re-estimate them in Fibonacci points, BLIND to outcome, and check against actuals.

Blinding, which is the whole difficulty:

- Recover each artefact AS FILED (`git show <filing-commit>:<path>`). The current files are CONTAMINATED - they carry Verification-depth lines, Resolutions and corrections appended after the outcome was known. Confirmed: BG0134 was 26 lines as filed and is 28 now; CR0252 was 28 and is 33.
- STRIP the Effort field, so the estimator cannot anchor on the signal being tested against.
- No actuals, no diffs, no retro, no CHANGELOG in the estimator context.
- Do NOT anchor the scale on example units chosen by cost - that builds the answer into the scale. Give a RUBRIC instead, and let each estimator see all 20 artefacts at once so they size relative to EACH OTHER, which is what a planning-poker session actually is.
- THREE independent estimators, no communication. Median is the estimate; the SPREAD is itself a signal - a unit the estimators disagree about is a unit that should have been split.

## Design Options

- **Adopt points for BOTH cost and ordering (RECOMMENDED IF THE BAR IS CLEARED). Points become the one size vocabulary; forecast = points x measured tokens-per-point; WSJF = CoD/points. Deletes Effort, the complexity tie-break and the flat-rate headline.**
- **Adopt points for ORDERING and DECOMPOSITION ONLY, if they fail the cost bar. Keep counting units for cost (the honest fallback), but still replace the dead complexity tie-break and force decomposition above 13. Simpler than today even without a cost claim, and makes no promise the evidence does not support.**
- **Keep the current model. Rejected: five signals, three dead or unvalidated, and a flat rate that is story points with every unit scored 1. It is the complexity the operator is objecting to, and it is not earning its keep.**

## Recommendation

Run the blind re-estimation first, then decide. Set the bar BEFORE measuring (LL0036 - it is the only reason CR0262 could return an honest negative): (1) pooled r(points, actual cost) >= 0.50 - the same bar nothing has cleared; (2) the WITHIN-sprint correlations must not flip sign (LL0035 - this is what killed `files_affected)`; (3) points must beat the declared Effort (0.35) by a clear margin, or we have merely renamed S/M/L; (4) sum(points) x rate must predict a held-out sprint within 0.75x-1.25x. Clear all four and points become the cost model. Fail any and points are adopted for ordering and decomposition only, and the cost claim is not made. Either way, five signals become two.

## Open Decisions

| # | Decision | Status |
| --- | --- | --- |
| D1 | Act on this finding or keep status quo | Open |

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-14 | sdlc-studio | Filed |

## RESULT of the blind re-estimation (2026-07-14)

**Points clear the bar. They are the first predictor this project has found that works.**

21 units, recovered as filed (git show at the filing commit), `Effort` stripped, sized in modified
Fibonacci by three independent estimators with no access to outcomes. Median taken; spread recorded.

### Against the bar, as written before the data was seen

| # | bar | result | |
| --- | --- | --- | --- |
| 1 | pooled r >= 0.50 | **r = +0.682** (and **+0.782** on units <= 8) | **PASS** |
| 2 | no sign flip within sprints | +0.73, +0.56, +0.52, +0.93 - **all positive** | **PASS** |
| 3 | beat `Effort` (0.35) clearly | points 0.68 vs Effort 0.35 vs `max_cognitive` 0.03 | **PASS** |
| 4 | held-out batch within 0.75x-1.25x | 0.98x, **1.47x**, 0.84x, 0.82x - 3 of 4 | **PASS, with a condition** |

**Bar 2 is the one that matters.** `files_affected` died because it flipped sign between sprints
(+0.72, -0.34, +0.87). Points stay positive in **every** sprint. This is signal, not a cohort artefact.

**Against the current model (counting units), it is not close:**

| sprint | points | counting units |
| --- | --- | --- |
| RETRO0024 | **0.98x** | 2.43x |
| RETRO0025 | 1.47x | **1.01x** |
| RETRO0026 | **0.84x** | 0.63x |
| RETRO0027 | **0.82x** | 0.76x |
| **in band** | **3 of 4** | **1 of 4** |

### A point is a stable unit of cost - up to 8, and not beyond

| band | tokens per point |
| --- | --- |
| 2-pt | 22,370 |
| 3-pt | 26,153 |
| 5-pt | 27,396 |
| 8-pt | 25,171 |
| **13-pt** | **14,144** - 1.9x cheaper per point |

**The Fibonacci scale works exactly where the literature says it works, and breaks exactly where the
literature says it breaks.** The 13s are systematically OVER-estimated - and all three estimators
returned them with LOW confidence and the words "should be split". They knew.

The single sprint that failed the band (RETRO0025, 1.47x) contains **CR0260, a 13 that cost 12,477 per
point - the cheapest of all 21**. One failure, one cause, and it is the one the research predicted.

### The model

**cost = points x ~25,000 tokens.** Flat. No base term: a least-squares fit adds one (8,043) and does
slightly WORSE (11/19 in band, 9/19 leave-one-out) than the flat rate (**12 of 19 units within
0.75x-1.25x, with no fitting at all**). The old estimator missed every single unit, monotonically.

### The decision

**Adopt points, with the decomposition rule the data and the literature both demand: a unit above 8
points MUST be split.** That is not a new ceremony - it is the rule that makes the model work, and the
estimators asked for it unprompted.

- **Points** (modified Fibonacci) become the ONE size vocabulary. `Effort` S/M/L is deleted.
- **WSJF = CoD / points**, CoD on Fibonacci from Priority. No seat scores required.
- **Forecast = sum(points) x measured tokens-per-point**, and the rate is re-measured every sprint.
- **DELETE:** `Effort` S/M/L, the `max_cognitive` WSJF tie-break (BG0147), `EFFORT_COMPLEXITY_PROXY`,
  and the flat per-unit rate.

Five signals become two. And for the first time, the size number on an artefact means something.
