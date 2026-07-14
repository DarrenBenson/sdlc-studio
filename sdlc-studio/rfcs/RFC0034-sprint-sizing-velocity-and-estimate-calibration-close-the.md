# RFC-0034: Sprint sizing, velocity and estimate calibration: close the estimate -> deliver -> recalibrate loop

> **Status:** Draft
> **Created:** 2026-07-14
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1

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

Lean **A**. It is the only option that answers all three of the operator's questions, and it uses
the unit an agent sprint actually terminates on. But the decisions below are real - this is raised to
be worked, not actioned; the freeze gives it time. CR0257 becomes its estimate-side workstream.

## Open Decisions

| # | Decision | Status |
| --- | --- | --- |
| D1 | **The canonical size unit.** Reconcile Effort S/M/L, story points, complexity, and tokens. Is there one canonical estimate unit, or a documented mapping between them (e.g. S/M/L -> a token band via measured history)? Bugs need a size too (CR0257). | Open |
| D2 | **How is "actual" measured at close?** Tokens (telemetry already records per-run tokens), wall-clock, unit-count, or delivered-effort-sum? The measure has to be cheap and automatic or the retro will not carry it. | Open |
| D3 | **Capacity target - value, unit, and owner.** Is there a per-sprint budget? In what unit (tokens/wall-clock, per the recommendation)? Who sets it, and does it feed CR0225's appetite defaults so plan-time capacity and run-time appetite agree? | Open |
| D4 | **The retro records estimate-vs-actual and accuracy** (the measure half). A `retro.py` + template enhancement: capture estimated size, actual, and the ratio; accumulate a velocity/accuracy history the next plan can read. | Open |
| D5 | **Do story points stay?** Keep points as a within-story human sizing aid feeding the canonical unit, or retire them in favour of one axis? Avoid a fourth vocabulary that also does not reconcile. | Open |

## Workstream (spawned on acceptance)

- **CR0257 (filed):** the estimate side - `Effort`/complexity feed the planner; bugs get a size.
- **CR (D4):** retro records estimated-vs-actual and accuracy; velocity history accumulates.
- **CR (D3):** a capacity model in tokens/wall-clock, wired to CR0225's appetite defaults.

## Related

RFC0032 (the learning loop the retro already runs - calibration is a natural sibling), CR0225
(appetite-bounded runs - the run-breaker units), CR0257 (sizing inputs), CR0253 (the review gate;
another close-time deterministic signal).

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-14 | sdlc-studio | Created via `new` (deterministic) |
