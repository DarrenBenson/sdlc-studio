# RETRO-0104: The twelve units delivered outside an approved batch

> **Date:** 2026-08-17
> **Batch:** BG0486, BG0509, BG0519, BG0526, BG0529, BG0545, BG0552, BG0553, BG0556, BG0571, BG0577, BG0582
> **Goal:** Account for twelve delivery units that reached a terminal status inside a run whose approved batch never named them, so the close-owed ledger reads zero because it is zero rather than because nobody looked.
> **Delivered:** 12 / 12   **Blocked:** 0

## Delivered

Nothing was BUILT here. All twelve units were delivered, reviewed and signed off inside earlier
runs; what was missing is the account, and this retro is that account rather than a claim of work.

**Eleven landed inside RUN-01KZQ03V** (closed goal-reached, RETRO0102, batch of 19) and **one
inside RUN-01M05A5M** (closed goal-reached, RETRO0103, batch of 12). In each case the unit was
delivered while the run was open and its id was never added to the run's batch, so no retro's
`Batch` line named it and `close_owed detect` reported a close owed for work that had in fact been
closed - twice over, since both runs did close.

* **BG0486, BG0509, BG0519, BG0526, BG0529, BG0577** - one commit, `f79e0d38`, the agreed
  bug-clearing sweep. Six units in a single subject line, none of them in the batch of 19.
* **BG0545, BG0552, BG0553** - `30232b3b`, the round-two repairs after an independent pass
  rejected four units. Repairs raised BY a review, which is exactly the work that arrives after a
  batch is fixed and is hardest to remember to add to it.
* **BG0556** - `734c775c`, landed alongside the SC0005 grooming work.
* **BG0571** - `8b808f8d`, the commit that CLOSED RUN-01KZQ03V. Delivered by the close itself.
* **BG0582** - `439eec6f`, this session's rung repair, delivered during RUN-01M05A5M on the
  operator's instruction and deliberately kept out of that run's design-rung batch.

## Blocked / deferred

* Nothing blocked. Every unit here was already terminal before this retro was written.
* **BG0579 and BG0580 are NOT in this batch**, and the distinction is the tool's, not mine:
  `close_owed detect` reports them as raised AND delivered inside a run whose close already ran,
  so no close is owed for them at all. Adding them here would have inflated the account by two
  units to make a number look tidier.

## What went well

* **The detector found this at all.** Nothing else did. Two runs closed clean, both retros
  validated, both gates passed - and twelve delivered units sat outside every batch line in the
  repository. `close_owed detect` is the only reason this is a retro rather than a permanent hole.
* **It distinguishes the two shapes.** Units raised and delivered inside a closed run owe nothing
  and are named separately from those that owe a close. A detector that lumped them together would
  have demanded ceremony for BG0579/BG0580 that nothing requires.
* The account cost one retro. The work was already done, reviewed and signed off; only the ledger
  was behind.

## What was hard / what stalled

* **The batch is a plan, and delivery kept outrunning it.** Every one of these twelve arrived the
  same way: work that was agreed mid-run - a sweep the operator asked for, repairs a review
  demanded, a fix instructed during a close - and `sprint batch --add` was never run for it. The
  gate that would have caught it does not exist, because a batch is approved once and then only
  read.
* **Three of the twelve were raised BY a review round.** That is the systematic case rather than
  the careless one: a review rejects, repairs land, and the repairs are new units nobody planned.
  The moment a round-two repair gets its own id is the moment it needs adding to the batch.
* **One was delivered by the close itself** (BG0571, in the closing commit), which no batch could
  have named in advance without the close knowing what it was about to fix.

## Lessons

* A batch is approved once and then only read, so work agreed AFTER the approval never joins it.
  Twelve units reached terminal inside runs whose batches never named them, and both runs still
  closed green - the close checks that the batch is accounted for, never that the account is the
  whole of what shipped.
* Repairs raised by a review round are new units nobody planned, and they are the systematic leak
  rather than the careless one. Three of these twelve were round-two repairs; the moment such a
  repair gets its own id it needs `sprint batch --add`, or the run that caused it will not name it.
* A ledger that reads zero because nobody looked is indistinguishable from one that reads zero
  because it is zero. The only reason this was visible is that a detector asked the question that
  no gate asks.

## Carried lessons

The 5 that matter most for the NEXT batch, chosen now rather than ranked from the whole
store. A ranking is a fact about the past; this is a decision, re-made every retro. Bullets,
not a numbered list, and drop one for each you add (`lessons carry --displaces`).

* Work agreed after the batch is approved must be added to it, or the run that caused it will
  not name it - twelve units proved this in two consecutive runs.
* A repair a review demands is a new unit, not a continuation of the one under review.
* Never repair the gate that is refusing your own run; record the wall and leave the run open.
* A mutant that cannot reach the code it names proves as little as a test that cannot fail.
* Parse the field, never the substring - a careless grep read `ac=3 pass=0` as three passing.

## Known issues carried

Every finding this sprint leaves OPEN, with the ruling somebody made on it. This is the one
compulsory close item the tree cannot derive: whether an open defect stops the ship is a
judgement, so it is recorded here and the sprint checklist reads it back. An open finding
with no row is reported as UNRULED, because "we carried it" and "nobody looked" must never
read the same.

Ruling is one of `stop-ship`, `not-stop-ship`, `accepted-risk`, `deferred`. A `stop-ship`
ruling HOLDS the close, which is the point of being able to make one.

None of these nine holds this account. Every one is a defect in the CLOSE ceremony or in a
detector, and this retro delivers no code at all - it records twelve units that were already
built, reviewed and signed off. BG0586 and BG0588 are the two to fix first: together they mean the
design rung's grooming bar accepts a run that groomed nothing, which is a real hole in a gate that
could not be passed at all yesterday.

| Issue | Ruling | Ruled by | Date |
| --- | --- | --- | --- |
| BG0581 | not-stop-ship | authoring session (recorded for the operator) | 2026-08-17 |
| BG0583 | not-stop-ship | authoring session (recorded for the operator) | 2026-08-17 |
| BG0584 | not-stop-ship | authoring session (recorded for the operator) | 2026-08-17 |
| BG0585 | not-stop-ship | authoring session (recorded for the operator) | 2026-08-17 |
| BG0586 | not-stop-ship | authoring session (recorded for the operator) | 2026-08-17 |
| BG0587 | not-stop-ship | authoring session (recorded for the operator) | 2026-08-17 |
| BG0588 | not-stop-ship | authoring session (recorded for the operator) | 2026-08-17 |
| BG0589 | not-stop-ship | authoring session (recorded for the operator) | 2026-08-17 |
| BG0590 | not-stop-ship | authoring session (recorded for the operator) | 2026-08-17 |

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
| BG0486 | - | - | - | **UNFORECAST** (no plan-time forecast recorded; no telemetry token record) | - | - | - | - |
| BG0509 | - | - | - | **UNFORECAST** (no plan-time forecast recorded; no telemetry token record) | - | - | - | - |
| BG0519 | - | - | - | **UNFORECAST** (no plan-time forecast recorded; no telemetry token record) | - | - | - | - |
| BG0526 | - | - | - | **UNFORECAST** (no plan-time forecast recorded; no telemetry token record) | - | - | - | - |
| BG0529 | - | - | - | **UNFORECAST** (no plan-time forecast recorded; no telemetry token record) | - | - | - | - |
| BG0545 | - | - | - | **UNFORECAST** (no plan-time forecast recorded; no telemetry token record) | - | - | - | - |
| BG0552 | - | - | - | **UNFORECAST** (no plan-time forecast recorded; no telemetry token record) | - | - | - | - |
| BG0553 | - | - | - | **UNFORECAST** (no plan-time forecast recorded; no telemetry token record) | - | - | - | - |
| BG0556 | - | - | - | **UNFORECAST** (no plan-time forecast recorded; no telemetry token record) | - | - | - | - |
| BG0571 | - | - | - | **UNFORECAST** (no plan-time forecast recorded; no telemetry token record) | - | - | - | - |
| BG0577 | - | - | - | **UNFORECAST** (no plan-time forecast recorded; no telemetry token record) | - | - | - | - |
| BG0582 | - | - | - | **UNFORECAST** (no plan-time forecast recorded; no telemetry token record) | - | - | - | - |
| **Batch (rated units only)** | **0** | **0** | **0** | - | **-** | | **-** | - |

**0 of 12 unit(s) measured; 0 of 12 forecast at plan time.**

**Velocity (points/elapsed-hour): UNMEASURED.** No run-state elapsed for this sprint (an interactive sprint's wall-clock would count operator-away gaps as sprint time). Supply a real elapsed with `accuracy --elapsed-hours H` to record it - descriptive, never a target.

  secondary (points/worker-hour): UNMEASURED - no runner worker-time records (an interactive sprint has none).

Review passes, by phase - read from the two verdict ledgers:

  test-plan review: NOT IN FORCE for this run - no verdict of that phase covers any of its units, which is not the same as a run that held them and spent nothing

  code review: 6 pass(es) over 4 unit(s), 5 rejected
Unforecast: BG0486, BG0509, BG0519, BG0526, BG0529, BG0545, BG0552, BG0553, BG0556, BG0571, BG0577, BG0582. No plan-time forecast was recorded for them, so they are excluded too. The estimate is NOT re-derived from today's constants: a number computed at judgement time, by the model being judged, is not a prediction.
No unit in this batch is rated, so this sprint says nothing about the estimator's accuracy.

Forecast by `-`, recorded at plan time. UNFORECAST: no plan-time forecast was recorded, so there is no prediction to judge. Nothing is re-derived to fill the gap.

Ratio is estimate / actual: above 1 the plan over-forecast, below 1 it under-forecast. Nothing is re-fitted here - see VELOCITY.md for the trend across sprints, and change the constants only on evidence a human has looked at.
<!-- accuracy:end -->

* Nothing, and that is the honest reading rather than a gap to apologise for. None of these
  twelve carried a plan-time forecast, because none was ever planned - that is the whole subject
  of this retro. `accuracy` reports all twelve UNFORECAST and re-derives nothing, which is right:
  a number invented now would be a prediction written after the result. The accuracy question is
  unanswerable for work that skipped the plan, and CR0546 is the fix for the cause rather than
  for the symptom.

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
| The batch is approved once and never re-checked, so mid-run work never joins it | CR0546 |
| Twelve units delivered outside a batch, found only by the detector | fixed-in: this retro accounts for all twelve |
| Whether `sprint batch --add` should be prompted at delivery rather than remembered | CR0546 |
| BG0579/BG0580 absent from RETRO0102's Batch line | declined: `close_owed` reports no close owed for them, and rewriting a closed run's batch to look complete would be the counted-fiction this retro exists to record |

<!-- file one with: scripts/file_finding.py · check with: scripts/retro.py dispose --id RETROxxxx -->

## Close loop (gated)

`gate --require-retro RETROxxxx` (this retro's id, file form) fails until all four are true:

* [x] this retro exists AND passes its content check - `retro.py validate --id RETRO0104` reports
      3 lessons and 4 findings all dispositioned
* [x] its lessons are in the project store - `retro.py extract --id RETRO0104` wrote L-0349 to L-0351
* [x] open lessons re-validated - 350 open, all within validity
* [x] `retros/LESSONS-SUMMARY.md` regenerated - 350 still-valid lessons

The next sprint reads them automatically: `sprint plan` prints the digest in the plan.

## Metrics

* Tokens: not-attributable - this retro accounts for work delivered across two earlier runs, and
  a session meter cannot be split between them after the fact · Duration: n/a, no work was built
  here · Critic rejects: 5 recorded across the twelve units, in the runs that delivered them
