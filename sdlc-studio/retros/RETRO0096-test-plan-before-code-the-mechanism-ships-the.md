# RETRO-0096: test-plan-before-code: the mechanism ships, the measurement lands next run

> **Date:** 2026-08-06
> **Batch:** {{batch}}
> **Goal:** {{goal}}
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

- **A retraction written only in prose is not a retraction.** US0632's AC3 was narrowed on a false premise, and correcting it in a comment block left `**Verified:** yes` on the line the tooling reads - `verify_ac` re-stamped it green from a test that does not exercise the property, so every mechanical reader still saw the criterion met. Setting the marker by hand did not survive either. The honest fix was to split the undelivered limb into a criterion with NO verifier, so the tool reports it unverified because it is. Write the retraction where the machine looks, or it has not happened.
- **A guard that reports the symptom and not the cause costs a day the first time and a command the second.** BG0528 was filed at the previous close, when twenty blockers named review coverage, sign-off and Done gates while the real fault was eight units still at `Ready`. It reproduced here exactly - and cost one command, because the message named it. Filing the diagnosis gap was worth more than fixing the instance.
- **The seat that reviews the plan should not be the one that trusts the author's mutation results.** Both seats independently re-derived the author's claims, and two of them were false: a mutant asserted killed had survived 2,137 tests, and a criterion's own rationale was factually wrong about the engine it described. Mutation results are claims until somebody else runs them.
- {{lesson}}   <!-- record it: lessons add (project tier). Promote with --global only what generalises beyond this repo -->

## Carried lessons

The 5 that matter most for the NEXT batch, chosen now rather than ranked from the whole
store. A ranking is a fact about the past; this is a decision, re-made every retro. Bullets,
not a numbered list, and drop one for each you add (`lessons carry --displaces`).

- A retraction written only in prose is not a retraction - write it where the machine looks.
- A test that passes for the wrong reason is worse than no test: force the failure at the boundary the guard actually holds.
- A repair breaks its neighbours, so after fixing one instance go looking for its twin.
- An enumerated list silently exempts what it forgot - derive the set, do not list it.
- Verify the premise before building on it, especially a premise about code you did not read.

## Known issues carried

Every finding this sprint leaves OPEN, with the ruling somebody made on it. This is the one
compulsory close item the tree cannot derive: whether an open defect stops the ship is a
judgement, so it is recorded here and the sprint checklist reads it back. An open finding
with no row is reported as UNRULED, because "we carried it" and "nobody looked" must never
read the same.

Ruling is one of `stop-ship`, `not-stop-ship`, `accepted-risk`, `deferred`. A `stop-ship`
ruling HOLDS the close, which is the point of being able to make one.

| Issue | Ruling | Ruled by | Date |
| --- | --- | --- | --- |
| BG0457 | deferred | Claude Opus 5 (author) | 2026-08-06 |
| BG0463 | deferred | Claude Opus 5 (author) | 2026-08-06 |
| BG0469 | deferred | Claude Opus 5 (author) | 2026-08-06 |
| BG0486 | deferred | Claude Opus 5 (author) | 2026-08-06 |
| BG0508 | deferred | Claude Opus 5 (author) | 2026-08-06 |
| BG0509 | deferred | Claude Opus 5 (author) | 2026-08-06 |
| BG0512 | deferred | Claude Opus 5 (author) | 2026-08-06 |
| BG0516 | deferred | Claude Opus 5 (author) | 2026-08-06 |
| BG0519 | deferred | Claude Opus 5 (author) | 2026-08-06 |
| BG0521 | deferred | Claude Opus 5 (author) | 2026-08-06 |
| BG0522 | deferred | Claude Opus 5 (author) | 2026-08-06 |
| BG0523 | deferred | Claude Opus 5 (author) | 2026-08-06 |
| BG0524 | deferred | Claude Opus 5 (author) | 2026-08-06 |
| BG0526 | deferred | Claude Opus 5 (author) | 2026-08-06 |
| BG0528 | deferred | Claude Opus 5 (author) | 2026-08-06 |
| BG0530 | deferred | Claude Opus 5 (author) | 2026-08-06 |
| BG0531 | deferred | Claude Opus 5 (author) | 2026-08-06 |
| BG0532 | deferred | Claude Opus 5 (author) | 2026-08-06 |
| BG0533 | deferred | Claude Opus 5 (author) | 2026-08-06 |
| BG0115 | deferred | Claude Opus 5 (author) | 2026-08-06 |
| BG0350 | deferred | Claude Opus 5 (author) | 2026-08-06 |
| BG0355 | deferred | Claude Opus 5 (author) | 2026-08-06 |
| BG0406 | deferred | Claude Opus 5 (author) | 2026-08-06 |
| BG0421 | deferred | Claude Opus 5 (author) | 2026-08-06 |
| BG0488 | deferred | Claude Opus 5 (author) | 2026-08-06 |
| BG0490 | deferred | Claude Opus 5 (author) | 2026-08-06 |
| BG0491 | deferred | Claude Opus 5 (author) | 2026-08-06 |
| BG0493 | deferred | Claude Opus 5 (author) | 2026-08-06 |
| BG0497 | deferred | Claude Opus 5 (author) | 2026-08-06 |
| BG0500 | deferred | Claude Opus 5 (author) | 2026-08-06 |
| BG0507 | deferred | Claude Opus 5 (author) | 2026-08-06 |
| CR0511 | deferred | Claude Opus 5 (author) | 2026-08-06 |
| CR0533 | deferred | Claude Opus 5 (author) | 2026-08-06 |
| CR0534 | deferred | Claude Opus 5 (author) | 2026-08-06 |

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
| **Batch (rated units only)** | **0** | **0** | **0** | - | **-** | | **-** | - |

**0 of 0 unit(s) measured; 0 of 0 forecast at plan time.**

Review passes, by phase - read from the two verdict ledgers:

  test-plan review: NOT IN FORCE for this run - no verdict of that phase covers any of its units, which is not the same as a run that held them and spent nothing

  code review: NOT IN FORCE for this run - no verdict of that phase covers any of its units, which is not the same as a run that held them and spent nothing
No unit in this batch is rated, so this sprint says nothing about the estimator's accuracy.

Forecast by `-`, recorded at plan time. UNFORECAST: no plan-time forecast was recorded, so there is no prediction to judge. Nothing is re-derived to fill the gap.

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
every EXAMPLE row; a row left in place is reported at the close, and a retro still carrying EVERY demonstration line this template ships is REFUSED by it.

| Finding | Disposition |
| --- | --- |
| The mutation engine applies a mutant at a different line from the one it enumerates | BG0533 |
| `verify_ac` reports a unit whose criteria it cannot parse as a clean pass | BG0530 |
| A delivered unit left at `Ready` is invisible to every close gate | BG0528 |
| `alias_map` decodes every artefact with a bare read_text | BG0532 |
| A hand-applied mutant is registered with no assertion its anchor was unique | BG0531 |
| `testplan derive` destroyed a hand-authored prose plan | fixed-in: ba543ee2 |
| Both new gates swallowed every exception and returned PASS | fixed-in: ba543ee2, 1573a8e7 |
| The plan-review brief printed no fingerprint while `record` demanded one | fixed-in: ba543ee2 |
| A judged batch could still be grown by an overlapping re-plan | fixed-in: ba543ee2 |
| An unreadable `.config.yaml` switched both new gates off | fixed-in: 1573a8e7 |
| US0632 AC4 - the mutant must be applied where it was enumerated | carried UNMET: BG0533 |

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
