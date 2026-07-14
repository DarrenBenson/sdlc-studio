# Unified Review - 2026-07-14 (close) - the axis sprint: the estimator was not mis-tuned, it was measuring nothing

> **Review type:** Sprint-close review (required by the `--require-review` gate, CR0253)
> **Reviewer:** sdlc-studio; agent; v1
> **Date:** 2026-07-14
> **Triggered by:** the sprint close - review currency is a hard gate
> **Project version:** 4.1.0 released; unreleased work on `main` under a freeze until ~2026-07-21

## Headline

**All 7 units delivered.** The headline result is a NEGATIVE one, and it is the most valuable thing the
project has produced: **no plan-time predictor of a unit's cost exists, so the per-unit forecast has been
dropped rather than replaced with a mediocre one.**

CR0262 set a bar BEFORE measuring - leave-one-out r >= 0.50, must beat the best single raw signal, ratio
within 0.5x-2.0x for most units. Nothing cleared it. The seed the forecast had been built on
(`max_cognitive`) scores **r = +0.03** against measured cost: both past recalibrations (5,000, then 600)
were fitting a slope through noise. **You cannot scale zero.**

The plan now leads with **batch history - what sprints ACTUALLY cost** - and quotes a flat measured rate
with a wide band, saying plainly: read the history, not this number.

**Two contaminants were found in the candidates that looked promising, and both were in numbers this
review previously reported as fact:**

| candidate | pooled r | the truth |
| --- | --- | --- |
| `files_affected` | +0.45 | **flips sign within sprints** (+0.72, -0.34, +0.87). A between-cohort artefact. |
| declared `Effort` | +0.47 | inflated. Scoring an undeclared Effort as zero makes the field's mere PRESENCE score +0.43 - the field only exists on later, larger units. **Honest value: +0.35.** |

The human estimate is still an order of magnitude better than anything the code computes about itself.
It is not what a naive pooled correlation claimed.

## The evidence is now durable, and the loop refuses to guess

- **BG0140:** the forecast and actuals logs moved out of gitignored `.local/` into tracked
  `retros/evidence/`. Proven by building a tree from `git ls-files` alone: all three sprints reproduce
  exactly. Before this, a fresh clone read UNFORECAST on every unit and the whole history read as
  no-evidence.
- **CR0263 + CR0261:** attribution on both sides of the ratio - who estimated, what delivered. **A batch
  spanning two models records no pooled ratio at all.** `unknown` is a first-class Effort value that
  cannot be coerced into a number, which is the structural fix for the contaminant above.
- **The coercion report says NOT ANSWERABLE.** Does a compulsory estimate become a careless one? On 5
  recorded estimates, where the compulsory cohort IS the latest cohort, the gate's effect cannot be
  separated from the calendar's. The tool reconstructed it offline, found it directionally consistent
  with the hazard, and **refused to quote it because n=4 says nothing.**

## The gate caught its own authors, again

- **BG0146 (HIGH, raised by this sprint's own verification):** CR0262 fitted its new rate on RETRO0025
  and RETRO0026's actuals, and their labels flipped to IN-SAMPLE with the generated text *"this ratio is
  TRAINING ERROR - it lands near 1.0x by construction"* - printed directly above **0.39x**. The claim
  refutes itself. Both were **genuine out-of-sample falsifications** and they are the entire evidence for
  dropping the forecast. **A recalibration relabelled the evidence that caused it** - BG0133's disease
  through a different door.
- **BG0144 (HIGH):** the grooming gate accepts an `Affects` naming files that DO NOT EXIST, and sizes the
  unit from the flat floor. Two of this session's own bug reports carried invented paths.
- **BG0137:** 361 archived index row links, every one a 404 - and the link guard had been *accommodating*
  them.

## This sprint's own accuracy

Forecast **494,000**, measured **789,591** across 5 of 7 units, ratio **0.44x** - labelled
**stale-constants**, because CR0262 replaced the estimator mid-sprint. It judges the model that died in
it and is correctly excluded from judging the one that replaced it. Two days ago this would have silently
re-derived every forecast and reported a comfortable ratio.

Two units (CR0261, BG0141) are **UNMEASURED** because they were folded into a third's agent to dodge a
file collision. Self-inflicted: merging units destroys per-unit measurement, and makes units bigger and
less uniform - the opposite of what the evidence says to do.

**The new flat rate has NO out-of-sample evidence yet.** Its first honest test is the next sprint, whose
forecast (720,000 for 6 units) is already recorded and cannot be re-derived.

## Backlog rollup (13 non-terminal)

- **Bugs (5):** BG0146 (High - the relabelling regression), BG0144 (High - fictional `Affects`), BG0142,
  BG0145 (Low), BG0143 is Fixed
- **CRs (4):** CR0264 (duplicate detection), CR0254, CR0255, CR0256 (the RFC0033 audit workstream)
- **RFCs (4, Proposed/Draft):** RFC0035 (the sprint report), RFC0036 (unattended multi-sprint), RFC0037
  (backlog triage - the ceremony that would have caught this sprint's three duplicate pairs)

**Recommended next batch:** BG0146 first - until it lands, the velocity history mislabels its own
evidence. Then BG0144. **Do not enable model routing yet** - the router's confidence handling is fixed
(CR0262) but it has never been validated against outcomes.

## For a fresh session

Start here, then `AGENTS.md`. The specs are current (CR0252). Read `RETRO0027` for why the per-unit
forecast was dropped, and LL0035 (a signal that flips sign between cohorts is not a predictor) and LL0036
(set the bar before you measure) before proposing any new estimator.

**The estimation strategy is now a work-shaping strategy.** Units vary 5.5x in cost (42,687 to 234,091),
and counting units is exactly as good a forecast as the units are uniform. The way to improve the forecast
is not a cleverer model - it is smaller, more uniform units. The breakdown gate and RFC0037's
oversized-unit lens ARE the estimation roadmap now.
