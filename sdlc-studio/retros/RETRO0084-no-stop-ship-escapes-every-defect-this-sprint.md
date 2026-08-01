# RETRO-0084: No stop-ship escapes: every defect this sprint creates is found and fixed inside the sprint by a review at each batch boundary, so the close certifies work already reviewed instead of discovering it, and no blocking defect is open at sign-off

**SUPERSEDED by [RETRO-0085](RETRO0085-run-01kypz1g-the-close-found-four-stop-ships.md) on 2026-07-31.**
This is an abandoned first scaffold for RUN-01KYPZ1G: it carries the same Batch line, the same
Goal, and no replaced content - every field below is still the template's placeholder. RETRO0085
is the filled retro for that run. **It records no delivery of its own and writes no VELOCITY
row**; a row here would double-count RETRO0085's 37 units into the rate the planner quotes.

It is kept rather than deleted because it is the evidence for BG0459: `retro validate` reports
this file `ok` and demotes the unreplaced-scaffold finding to a warning, and `sprint close`
discards that warning on a zero exit (BG0418). A wholly empty retro passing the content gate is
the defect, and this is the specimen.

> **Date:** 2026-07-30
> **Batch:** BG0402, BG0403, BG0404, BG0405, BG0407, BG0411, BG0412, BG0414, BG0416, US0452, US0453, US0454, US0455, US0456, US0457, US0458, US0459, US0460, US0461, US0462, US0463, US0464, US0465, US0476, US0477, US0478, US0484, US0485, US0486, US0560, US0561, US0562, US0563, BG0441, BG0450, BG0453, BG0446
> **Goal:** No stop-ship escapes: every defect this sprint creates is found and fixed inside the sprint by a review at each batch boundary, so the close certifies work already reviewed instead of discovering it, and no blocking defect is open at sign-off
> **Delivered:** {{n_done}} / {{n_total}}   **Blocked:** {{n_blocked}}

## Delivered

- {{unit}} - {{what_shipped}}

## Blocked / deferred

- {{unit}} - {{blocker}}

## What went well

- {{good}}

## What was hard / what stalled

- {{hard}}

## Lessons

- EXAMPLE - replace this. A lesson is a transferable claim with the evidence that produced it, not a task: "a test that asserts a label rather than the value proves the tool named its state, not that it reached it - two of this sprint's three mutation survivors were exactly that". <!-- example -->
- {{lesson}}   <!-- record it: lessons add (project tier). Promote with --global only what generalises beyond this repo -->

## Carried lessons

The 5 that matter most for the NEXT batch, chosen now rather than ranked from the whole
store. A ranking is a fact about the past; this is a decision, re-made every retro. Bullets,
not a numbered list, and drop one for each you add (`lessons carry --displaces`).

- EXAMPLE - replace this. A mechanism that reaches no caller is inert, however well it is tested. <!-- example -->
- EXAMPLE - replace this. An absence is not an answer: an empty result and an unanswerable question are different facts. <!-- example -->
- EXAMPLE - replace this. A repair breaks its neighbours, and a rename is cross-unit coupling. <!-- example -->
- EXAMPLE - replace this. An enumerated list silently exempts what it forgot. <!-- example -->
- EXAMPLE - replace this. Verify the premise before building on it. <!-- example -->

## Estimate vs actual

**Were the estimates any good?** The plan forecast a token cost per unit; telemetry recorded
what each one actually cost. This section holds the comparison, so the question is asked every
sprint instead of only when someone remembers to ask it.

Generate it: `scripts/retro.py accuracy --id RETROxxxx --write` - it fills the block below from
the batch's telemetry and appends this sprint's row to `retros/VELOCITY.md`.

A unit with no per-unit telemetry record has its PER-UNIT ratio reported as **UNMEASURED** and
excluded from that ratio - it is never counted as accurate. But the token count itself is NOT
unmeasurable: the harness tracks it deterministically. An INTERACTIVE sprint (no runner) records no
per-unit actual, so the close captures this RUN's share of the harness-tracked total itself
(`accuracy --tokens-from-harness`, run by `sprint close --apply-signoff`) and the velocity row
records it. The meter is per-SESSION and cumulative, so what is captured is the delta from the
baseline stamped when the run opened - not the session total, which in a session holding more than
one sprint counts the earlier ones again. A run with no baseline (opened before the baseline
existed, or closed from a different session) reports **not-attributable** rather than a number:
there is no fallback to the raw total, because a plausible-looking figure that is not this sprint's
cost is worse than an absent one. When the capture cannot attribute, the close states why and
`accuracy --tokens N` remains the manual override.
Report it as **not-yet-captured** only while neither has happened, never as if the number were
unknowable. That figure is DESCRIPTIVE, never a target (see CR0273).

The forecast is a hypothesis, not a settled calibration. Read the ratio, write down what it
implies, and change the constants only on evidence a human has looked at - a fit to a couple of
sprints fits noise.

<!-- accuracy:begin (generated by retro.py accuracy --write) -->

| Unit | Points | Estimate (plan-time) | Actual | Ratio (est/actual) | Tokens/pt | Size | Wall | Model |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| BG0402 | - | - | - | **UNFORECAST** (no plan-time forecast recorded; no telemetry token record) | - | - | - | - |
| BG0403 | 3 | 138,429 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| BG0404 | 2 | 92,286 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| BG0405 | 2 | 92,286 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| BG0407 | 3 | 138,429 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| BG0411 | 3 | 138,429 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| BG0412 | 2 | 92,286 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| BG0414 | 2 | 92,286 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| BG0416 | 2 | 92,286 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| US0452 | 3 | 138,429 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| US0453 | 5 | 230,715 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| US0454 | 3 | 138,429 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| US0455 | 3 | 138,429 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| US0456 | 5 | 230,715 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| US0457 | 3 | 138,429 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| US0458 | 3 | 138,429 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| US0459 | 3 | 138,429 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| US0460 | 5 | 230,715 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| US0461 | 5 | 230,715 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| US0462 | 3 | 138,429 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| US0463 | 5 | 230,715 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| US0464 | 5 | 230,715 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| US0465 | 5 | 230,715 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| US0476 | 2 | 92,286 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| US0477 | 3 | 138,429 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| US0478 | 3 | 138,429 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| US0484 | 5 | 230,715 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| US0485 | 5 | 230,715 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| US0486 | 3 | 138,429 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| US0560 | 5 | 230,715 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| US0561 | 3 | 138,429 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| US0562 | 5 | 230,715 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| US0563 | 3 | 138,429 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| BG0441 | - | - | - | **UNFORECAST** (no plan-time forecast recorded; no telemetry token record) | - | - | - | - |
| BG0450 | - | - | - | **UNFORECAST** (no plan-time forecast recorded; no telemetry token record) | - | - | - | - |
| BG0453 | - | - | - | **UNFORECAST** (no plan-time forecast recorded; no telemetry token record) | - | - | - | - |
| BG0446 | - | - | - | **UNFORECAST** (no plan-time forecast recorded; no telemetry token record) | - | - | - | - |
| **Batch (rated units only)** | **0** | **0** | **0** | - | **-** | | **-** | - |

**0 of 37 unit(s) measured; 32 of 37 forecast at plan time.**

**Velocity (points/elapsed-hour): UNMEASURED.** No run-state elapsed for this sprint (an interactive sprint's wall-clock would count operator-away gaps as sprint time). Supply a real elapsed with `accuracy --elapsed-hours H` to record it - descriptive, never a target.

  secondary (points/worker-hour): UNMEASURED - no runner worker-time records (an interactive sprint has none).
Unmeasured: BG0403, BG0404, BG0405, BG0407, BG0411, BG0412, BG0414, BG0416, US0452, US0453, US0454, US0455, US0456, US0457, US0458, US0459, US0460, US0461, US0462, US0463, US0464, US0465, US0476, US0477, US0478, US0484, US0485, US0486, US0560, US0561, US0562, US0563. They are excluded from the batch ratio - an unmeasured unit is not evidence that the estimate was right.
Unforecast: BG0402, BG0441, BG0450, BG0453, BG0446. No plan-time forecast was recorded for them, so they are excluded too. The estimate is NOT re-derived from today's constants: a number computed at judgement time, by the model being judged, is not a prediction.
No unit in this batch is rated, so this sprint says nothing about the estimator's accuracy.

Forecast by `TOKENS_PER_POINT=25000`, recorded at plan time. OUT-OF-SAMPLE: forecast by the constants in force, on a sprint they were not fitted to. This is the only kind of row that tells you anything.

Ratio is estimate / actual: above 1 the plan over-forecast, below 1 it under-forecast. Nothing is re-fitted here - see VELOCITY.md for the trend across sprints, and change the constants only on evidence a human has looked at.
<!-- accuracy:end -->

- {{what the ratio implies - which units the estimate missed, and why}}

## Actions raised

**Are there any CRs or Bugs you want to raise in this project to address any of the
issues found?**

This is the question that turns a retro into work. Every finding gets a disposition:
**file it** (a BG/CR id), **record it fixed in-sprint** (`fixed-in: <sha or unit>`), or
**decline it with a reason**. All three are green. What does not pass is silence - a
finding written down and left to rot. The three are counted separately at close: a sprint
that repaired eleven findings reads as eleven fixed, not eleven declined.

To say "nothing worth raising", say so in a row and give the reason. An empty table is
not an answer.

All three accepted dispositions are shown below, filled in rather than described - the
vocabulary is exact and a refusal is a poor place to meet it for the first time. Replace
every EXAMPLE row; a row left in place is reported at the close.

| Finding | Disposition |
| --- | --- |
| EXAMPLE - replace this. A defect worth its own artefact | BG0123 |
| EXAMPLE - replace this. A defect repaired inside this sprint | fixed-in: a1b2c3d |
| EXAMPLE - replace this. A finding not worth acting on | declined: the cost lands on a path this project does not use |

<!-- file one with: scripts/file_finding.py · check with: scripts/retro.py dispose --id RETROxxxx -->

## Close loop (gated)

`gate --require-retro RETROxxxx` (this retro's id, file form) fails until all four are true:

- [ ] this retro exists AND passes its content check - required sections, at least one real
      lesson, and every finding dispositioned (`retro.py validate --id RETROxxxx`)
- [ ] its lessons are in the project store, not just in this file (`retro.py extract --id RETROxxxx`)
- [ ] open lessons re-validated: each is closed, extended, or within its horizon (`lessons revalidate`)
- [ ] `retros/LESSONS-SUMMARY.md` regenerated from the still-valid lessons (`lessons summary`)

The next sprint reads them automatically: `sprint plan` prints the digest in the plan.

## Metrics

- Tokens: {{tokens}} · Duration: {{duration}} · Critic rejects: {{rejects}}
