# RFC-0034: Sprint sizing, velocity and estimate calibration: close the estimate -> deliver -> recalibrate loop

> **Status:** Accepted (partially superseded)
> **Created:** 2026-07-14
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Partially superseded by:** [RFC-0038](RFC0038-simplify-to-fibonacci-story-points-and-real-wsjf.md) - decisions **D1** (the canonical size unit) and **D5** (do story points stay?) are overtaken. RFC-0038 makes modified-Fibonacci story points the ONE size vocabulary, deletes Effort S/M/L, and sums points as measured velocity - so tokens are no longer the canonical estimation unit and points are no longer a within-story alias. **D2-D4 remain live:** RFC-0038's model depends on the actual-measurement (D2), capacity (D3) and retro-accuracy (D4) machinery this RFC defines.

## Summary

Surfaced while planning the internal-hardening sprint: the operator asked how sizing works, whether
the estimates were accurate, and how much belongs in a sprint - and none of the three has an answer,
because the project has **no estimate -> deliver -> recalibrate loop**. It estimates unevenly, never
measures actual against estimate, and has no velocity or capacity baseline.

### Three disconnected size vocabularies

| Where | Unit | Read by the planner? |
| --- | --- | --- |
| Stories | story points (`max_points` 13 per story) | no |
| CRs | `Effort: S/M/L` (captured at filing) | **no** (CR0257) |
| Bugs | nothing - only Severity (which is priority, not size) | n/a |
| Planner | cognitive complexity of a unit's `Affects` files + a token forecast | yes, when `Affects` is declared |
| Runs | tokens / wall-clock / unit-count appetite + circuit breaker (CR0225) | this is the actual run-breaker |

They do not reconcile. The estimate a human records (`Effort`) does not feed the estimator; the
estimator's input (`Affects`) is usually absent; and the thing that actually bounds a run (tokens /
wall-clock) is a fourth unit nobody estimates in.

### The gap, in three halves

- **Estimate** is not fed to the planner - CR0257 (filed) fixes the `Effort`/complexity half.
- **Actual** is never measured. The retro records `Delivered N/M` (a count) and tokens/duration, but
  never estimated-vs-actual size, so accuracy is unknowable and velocity never accumulates.
- **Capacity** has no target and no unit. "How many story points per sprint?" has no answer here,
  and probably the wrong unit: points are a human-team effort proxy, but an agent sprint hits a
  **tokens / wall-clock** wall, not a points wall. CR0225's appetite already speaks that language.

Evidence, from one session: the 10-unit plan forecast a flat ~500k (= 50k x 10, complexity zero
because no unit declared `Affects`), while CR0257 - once given an `Affects` line - forecast ~195k,
complexity actually informing the number. The machinery works; it is starved of input and its
output is never checked against reality.

## Design Options

- **A - Full loop, tokens/time as the capacity unit (recommended direction).** Estimate feeds the
  planner (CR0257); the retro records estimated-vs-actual and computes accuracy; velocity accumulates
  across retros; capacity is expressed in tokens / wall-clock / unit-count (the real run-breaker,
  CR0225's units), with story points kept only as a within-story human aid. One loop, one capacity
  unit that matches how agent runs actually end.
- **B - Estimate side only.** Ship CR0257 and stop - make sizing informed, but do not measure actual
  or track velocity. Cheaper, but it never answers "were the estimates accurate?" - it just makes a
  better guess with no feedback.
- **C - Human story-point velocity.** Adopt classic story-point capacity (sum points per sprint,
  track velocity in points). Familiar, but points are the unit that fits this project worst - mixed
  artefact types, solo+agents, and a run that breaks on tokens/time, not points.

## Recommendation

Option **A accepted** - the full loop with tokens as the canonical unit. It is the only option that
answers all three of the operator's questions and it uses the unit an agent sprint actually
terminates on. All five decisions resolved below; they cohere into one design: **everything speaks
tokens.** Humans estimate in Effort S/M/L (points for stories), which map to calibrated token bands;
actual is read from telemetry (already logged per unit); the retro compares them; capacity is a
token/wall-clock budget wired to CR0225's appetite.

## Open Decisions

| # | Decision | Resolution | Status |
| --- | --- | --- | --- |
| D1 | The canonical size unit. | **[Superseded by [RFC-0038](RFC0038-simplify-to-fibonacci-story-points-and-real-wsjf.md).]** Original resolution: **Tokens are canonical.** Humans still estimate in Effort S/M/L (stories in points); those map to **calibrated token bands**. Bugs gain an effort field (CR0257). The bands ship **provisional** (a documented S/M/L -> token default) and are **recalibrated from velocity history** once D4 accumulates it. RFC-0038 replaced this: modified-Fibonacci story points are the one size vocabulary, Effort S/M/L is deleted, and the forecast is points x measured tokens-per-point. | Superseded (RFC-0038) |
| D2 | How "actual" is measured at close. | **Wall-clock from telemetry; tokens need a supplier (corrected).** `telemetry.py` has the `tokens` and `wall_time_s` FIELDS, but only wall-clock is measurable by the loop - a Python helper cannot observe LLM token spend (`sprint.py` says so in a comment), and in practice **the `tokens` field has never been populated: 330 telemetry records, zero token values**. So the measure half is ~80% built for wall-clock and ~0% for tokens: the field exists, the meter does not. The token actual must be SUPPLIED - the concrete path is to run each unit as an instrumented subagent and record its reported usage into `artifact.py close --tokens` (in CR0258). Wall-clock is the reliable actual until that lands. | Decided |
| D3 | Capacity target - value, unit, owner. | **An operator-set per-sprint budget in tokens + wall-clock, wired to CR0225's appetite defaults**, so the plan-time "does this fit" and the run-time circuit-breaker are the same number. Provisional default now; recalibrated from velocity. | Decided |
| D4 | The retro records estimate-vs-actual + accuracy. | **Yes** - `retro.py` + template read telemetry actuals against the plan's estimate, record the ratio, and accumulate a velocity/accuracy history the next plan reads. This is the keystone: it produces the data that calibrates D1's bands and D3's budget. | Decided |
| D5 | Do story points stay? | **[Superseded by [RFC-0038](RFC0038-simplify-to-fibonacci-story-points-and-real-wsjf.md).]** Original resolution: **Kept as a within-story human aid that maps to a token band** - not summed for capacity. Points become an alias into the canonical unit, not a fourth vocabulary. RFC-0038 reversed this: points are no longer an alias but the canonical size unit itself, and they ARE summed - velocity is points delivered per sprint. | Superseded (RFC-0038) |

## Workstream (spawned on acceptance)

D4 is the keystone - it produces the history that calibrates D1's bands and D3's budget - so the
estimate and capacity pieces ship with **provisional** bands/defaults first and calibrate once the
history exists. It is a public-behaviour change to planning and the retro, so it lands under the
freeze on `main` and ships with v4.2, not this week.

- **CR0257 (filed):** estimate side - `Effort`/complexity feed the planner with a provisional
  S/M/L -> token-band mapping; bugs get an effort field.
- **CR (D4, keystone):** the retro reads telemetry actuals against the plan estimate, records
  accuracy, and accumulates a velocity history; recalibrates the S/M/L token bands from it.
  **Includes the token supplier** (corrected premise): tokens are never auto-measured, so this CR
  must also make the loop record a real token actual - run each unit as an instrumented subagent
  and feed its reported usage into `artifact.py close --tokens`. Wall-clock works today; tokens do
  not until this lands.
- **CR (D3):** a capacity model in tokens/wall-clock, operator-set, wired to CR0225's appetite
  defaults. Depends on the D4 history to move off the provisional default.

## Related

RFC0032 (the learning loop the retro already runs - calibration is a natural sibling), CR0225
(appetite-bounded runs - the run-breaker units), CR0257 (sizing inputs), CR0253 (the review gate;
another close-time deterministic signal),
[RFC-0038](RFC0038-simplify-to-fibonacci-story-points-and-real-wsjf.md) (supersedes D1 and D5 -
modified-Fibonacci story points, not tokens, become the canonical size unit; D2-D4 remain live).

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-14 | sdlc-studio | Created via `new` (deterministic) |
| 2026-07-17 | sdlc-studio | Partial supersession recorded: D1 and D5 overtaken by RFC-0038 (points, not tokens, are canonical); header note, D1/D5 rows and Related cross-link added; D2-D4 remain live |
