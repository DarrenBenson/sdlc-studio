# RETRO-0025: The sizing sprint: the loop measured itself and the estimator failed

> **Date:** 2026-07-14
> **Batch:** CR0257, CR0258, BG0132, CR0259, CR0260
> **Goal:** close RFC0034 (sizing, velocity, calibration) and make the breakdown step unavoidable
> **Delivered:** 5 / 5   **Blocked:** 0

## Delivered

- CR0257 - the human `Effort:` (S/M/L) reaches the planner: WSJF job size when the seats have not
  scored a unit, and a complexity stand-in for the forecast when a unit names no files. A unit with
  real complexity is never inflated by its effort, so the measured model is untouched.
- CR0258 - the retro can ask whether the estimates were any good. `retro.py accuracy` reports the
  forecast against telemetry; `--write` appends the sprint's row to a committed `VELOCITY.md`. An
  unmeasured unit is reported UNMEASURED and excluded from both sides of the ratio, and nothing
  auto-recalibrates.
- BG0132 - the false-green class is dead. 49 command-shaped `Verify:` lines across 18 artefacts,
  none of which anything has ever executed, rewritten as statements of observable outcome. The filer
  now refuses a new one at creation.
- CR0259 - plan-time capacity and the run-time breaker are one number, resolved once at plan time and
  stamped on run state. Over-budget warns and never gates.
- CR0260 - the breakdown step is unavoidable. `sprint plan` refuses an ungroomed batch: exit
  non-zero, no plan printed. Shared-file clusters are derived from `Affects`, so two units touching
  the same file are no longer reported as safely parallel.

## Blocked / deferred

- Nothing blocked. Four new bugs were RAISED by the work: BG0133, BG0134, BG0135, BG0136.

## What went well

- Every unit was verified through the public path before its report was believed, and it paid for
  itself every time. The gate refusing BG0132 to Fixed for a missing verification depth, the filer
  refusing two hollow bugs, the orphan index row surviving three guards: none of that was in any
  subagent's report. It was found by re-running the work through the CLI an operator would use.
- The gates fired against their own authors. CR0260's breakdown gate, on its first run, refused three
  bugs filed that same day by our own filer. The retro gate refused a retro for an undispositioned
  finding.
- The false-parallel wave CR0260 was raised to catch was caught immediately, and one of the pairs it
  caught was CR0254/CR0260 - the CR that introduced the check.

## What was hard / what stalled

- The measurement loop was, at the outset, incapable of proving itself wrong. `accuracy` re-derives
  each estimate at retro time from the LIVE constants, so recalibrating them silently rewrites what
  every past sprint is deemed to have predicted. RETRO0024's 5.2x miss on BG0126 - the entire evidence
  that drove the recalibration - now re-reads as 1.57x. The error was erased by the fix it caused.
  That is BG0133, and it is a design error in the brief that was written, not in the delivery.
- The planner then began quoting the in-sample 1.09x back to the operator as the estimator's observed
  accuracy, while the out-of-sample figure was running at half that. The number that reassures was the
  one that could not be wrong.
- The filer cannot record `Affects` at all - there is no such flag - so every bug it writes is born
  unplannable and is then refused by our own planner (BG0136).

## Lessons

- An estimate re-derived at judgement time from the constants it is meant to be judging is not a
  prediction, and a loop built on one cannot be falsified. Record the forecast when it is MADE.
- Reporting a model's fit against the same data it was fitted to is training error, not validation. It
  lands near 1.0x by construction. Only a forecast made BEFORE the fit tells you anything.
- A gate belongs in the command people actually run, not in a step they are told to run. The design
  rung has been specified for months to produce an estimated backlog and has never once been invoked;
  the same grooming, enforced inside `plan`, was unavoidable on day one.
- When two tools judge the same artefact, they must agree on what a COMPLETE one is. The filer writes
  what the planner refuses, because the definition of groomed lives in only one of them.
- A calibration fitted to work delivered under one standard does not survive a change in the standard.
  This sprint's briefs demanded a failing test first, behavioural assertions and public-path
  verification; the work per unit grew accordingly, and the estimator was left chasing a target that
  had moved for reasons it cannot see.

## Estimate vs actual

**Were the estimates any good? No. The hypothesis is falsified.**

The forecast below is the one recorded at PLAN TIME, before any of this sprint's code existed. It is
not the number `retro.py accuracy` prints today - that tool re-derives estimates from the live
constants (BG0133), which is exactly the defect this table exists to expose.

| unit | est (plan-time) | actual | ratio | tool-uses |
| --- | --- | --- | --- | --- |
| CR0257 | 67,400 | 97,863 | 0.69x | 45 |
| CR0258 | 77,000 | 107,623 | 0.72x | 36 |
| BG0132 | 73,400 | 129,957 | 0.56x | 58 |
| CR0259 | 67,400 | 144,711 | 0.47x | 60 |
| CR0260 | 67,400 | 162,204 | 0.42x | 81 |
| **BATCH** | **352,600** | **642,358** | **0.55x** | 280 |

5 of 5 units measured.

`TOKENS_PER_COGNITIVE = 600` was fitted to six units and scored 1.09x in-sample. Out-of-sample it
scores **0.55x**: it under-forecasts every unit, and monotonically - the larger the job, the worse the
miss. The band the calibration test asserts is 0.75x to 1.25x, and this batch is outside it. The
previous coefficient (5,000) over-forecast by 3.3x; the new one under-forecasts by 1.8x. Both were
fitted to a single sprint, and both failed the next one.

The diagnosis is not "the coefficient is wrong", it is **"the predictor is wrong"**. Actual cost
correlates with tool-uses at r = 0.926 (about 2,294 tokens each) and barely with the cognitive
complexity of the files touched. Cost tracks the WORK DONE, and file complexity does not measure work
done: a small, well-scoped fix in a large file does not pay the whole file's complexity.

But tool-uses cannot serve as a forecast. It is an OUTPUT, known only once the work is finished. So
this is not a better constant waiting to be fitted; it is evidence that the input being forecast from
does not carry the signal.

**Do not re-fit to 11 points.** That is the mistake this sprint documented twice. What the evidence
supports is stated and no more: the model is a batch tool with a weak per-unit signal, it has now
failed in both directions on consecutive sprints, and the confound is real - this sprint's briefs
demanded more per unit than the six the constants were fitted to, so the estimator is chasing a
standard that moved.

## Actions raised

**Are there any CRs or Bugs you want to raise in this project to address any of the issues found?**

| Finding | Disposition |
| --- | --- |
| The accuracy report re-derives estimates from live constants and cannot falsify the estimator | BG0133 |
| The engagement-floor trailer check warns after the commit has landed, then exits 0 | BG0134 |
| reconcile is blind to an orphan index row whose artefact file is gone; three guards missed it | BG0135 |
| The filer cannot record Affects, so every bug it writes is refused by our own planner | BG0136 |
| The estimator is falsified out-of-sample at 0.55x; the predictor, not the coefficient, is wrong | declined: no ticket yet, deliberately. Re-fitting the constant now would fit noise to 11 points and repeat the error documented twice above. BG0133 must land first, so a forecast is recorded at plan time and a future sprint can be judged against what was actually predicted. Recalibration is the operator's decision, on evidence, once the loop can produce evidence. |
| Cognitive complexity of a file is a poor proxy for the work done in it | declined: this is the substance of the finding above, not a separate ticket. Recorded as a lesson. |

## Close loop (gated)

- [x] this retro exists AND passes its content check
- [x] its lessons are in the project store
- [x] open lessons re-validated
- [x] `retros/LESSONS-SUMMARY.md` regenerated

## Metrics

- Tokens: 642,358 (5 units, all measured) - Duration: 3,157s of worker time - Critic rejects: 0
