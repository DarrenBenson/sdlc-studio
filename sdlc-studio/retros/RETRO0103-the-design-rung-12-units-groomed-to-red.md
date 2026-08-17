# RETRO-0103: The design rung: 12 units groomed to RED criteria, and a goal review that rejected the first shape

> **Date:** 2026-08-16
> **Batch:** US0625, US0626, US0627, US0628, US0646, US0647, US0648, US0649, US0650, US0651, BG0490, BG0493
> **Goal:** No open delivery unit is unplannable: every one carries authored acceptance criteria whose Verify line executes and fails RED against the absent behaviour, rather than restating the finding.
> **Delivered:** 12 / 12   **Blocked:** 0

## Delivered

All 12 units groomed. `sprint breakdown` reports **0 ungroomed, down from 12**, and the ten
stories reached Ready - the design rung's own terminal. The two bugs stay Open with criteria,
which is the rung's product for a type whose vocabulary has no Ready.

**The red-now ledger, this rung's exit condition: 40 criteria, 0 pass, 40 fail, 0 manual, 0
unspecified.** Ten stories carry 33, the two bugs 7. That figure was wrong twice before it
was measured properly - 38 here, and a first re-measure that read `ac=3 pass=0` as "3 pass"
with a careless grep and reported all ten stories GREEN. Parse the field, never the substring. Zero passing is the column that matters. A criterion that passes before its
behaviour exists is the vacuous verifier the rung exists to catch, and RETRO0071 found three of
those in a comparable run. Zero unspecified means none dodged into `manual` or an unrunnable
line.

The mechanic was measured before a single criterion was written: a Verify line naming a test that
does not yet exist reports FAIL rather than `refused`, so "executes and fails red" is a claim
these criteria genuinely meet rather than a form of words.

## Blocked / deferred

* Nothing blocked. The batch is not safely parallel - two clusters over `pre-commit`, `critic.py`
  and `sdlc_md.py` - and was worked sequentially.
* **BG0581** filed rather than fixed: the goal-review brief states a reachable end state without
  knowing the rung, so it promised Review for a rung that ends at Ready.
* The TSD is stale, which the plan reported at open. Its risk areas derive from a document the
  code has moved past, and nothing in this run refreshed it.

## What went well

* **The adversarial goal review rejected the first shape of this run, and was right five times.**
  It ran BEFORE anything was planned, which is the only reason those five cost minutes instead of
  a close. QA's verdict was REJECT on the ground that nothing gated the goal, and that objection
  produced the red-now ledger.
* **The charter was amended rather than planned around.** SC0005's scope query is `--bugs Open`
  and its 20 named bug ids are all terminal, so it authorised none of this batch. A charter whose
  scope has emptied is not a licence for whatever batch is convenient.
* Six of the original sixteen needed nothing - 20 of 57 points already groomed. Counting them as
  delivery would have been the counted-fiction failure this charter's own re-measurement records.

## What was hard / what stalled

* **My own BG0556 control removed four inventory entries in two days**, three of them the moment
  this run opened. None was wrong to admit; the ADMISSION RULE was, because "names an artefact
  when pointed at the real tree" is a question whose answer moves with the tree. The bar is now
  unconditional.
* **The disclosure page and the release notes drifted apart three times in this session.** Each
  time the guard was right and each time the cause was the same: a derived page and a hand-written
  claim that can disagree, kept in step by my remembering.
* A stray non-Latin character reached a criterion I authored. Caught by re-reading, not by a lane
  * no guard covers it.

## Lessons

* An admission rule that asks a question whose answer moves with the tree admits entries that
  silently stop qualifying. Four inventory entries were removed in two days, each caught by the
  control rather than by anyone reading the list; none was wrong to admit, and every one passed
  its measurement honestly on the day it went in. Bars must be unconditional or they rot.
* A rung is a claim about what a run can reach, and stating a terminal without knowing the rung
  is stating an answer to a question nobody asked. The brief promised Review for a run that
  correctly ends at Ready (BG0581).
* A charter whose declared scope has emptied does not become a licence for whatever batch is
  convenient. SC0005 named 20 bug ids, all now terminal, and its scope query authorised no story
  at all - amend it on the record, or the run has no charter.
* An exit condition satisfied by deleting a marker is not an exit condition. `story_is_ungroomed`
  returns false the moment the placeholder token goes, so the goal needed evidence - the red-now
  ledger - rather than a gate that a `touch` clears.

## Carried lessons

* A mutant that cannot reach the code it names proves as little as a test that cannot fail.
* A mechanism that reaches no caller is inert, however well tested.
* Verification run where the author is standing is not verification.

The 5 that matter most for the NEXT batch, chosen now rather than ranked from the whole
store. A ranking is a fact about the past; this is a decision, re-made every retro. Bullets,
not a numbered list, and drop one for each you add (`lessons carry --displaces`).

## Known issues carried

Every finding this sprint leaves OPEN, with the ruling somebody made on it. This is the one
compulsory close item the tree cannot derive: whether an open defect stops the ship is a
judgement, so it is recorded here and the sprint checklist reads it back. An open finding
with no row is reported as UNRULED, because "we carried it" and "nobody looked" must never
read the same.

Ruling is one of `stop-ship`, `not-stop-ship`, `accepted-risk`, `deferred`. A `stop-ship`
ruling HOLDS the close, which is the point of being able to make one.

BG0583 is ruled `not-stop-ship` on evidence rather than on comfort: it lets `verify_ac run`
report success for a unit it never read, which is exactly the failure that would undermine this
run's red-now ledger - so the ledger was re-taken per unit and per PATH, and all twelve returned
a real `ac=/pass=/fail=` line. The evidence this run rests on was measured through the path that
works, not the one that lies.

BG0582 was ruled `not-stop-ship` when this table was written and was FIXED before the close, on
the operator's instruction. Its row stays as the record of the ruling that was made at the time.

BG0585 to BG0589 were all raised by the three adversarial rounds over BG0582's own repair, after
this table was first written. Every one is ruled `not-stop-ship` on the same reasoning: they are
defects in the CLOSE ceremony and the grooming bar, and this run's product is 12 groomed units
carrying 40 red criteria - a deliverable none of them touches. Two deserve naming, because ruling
them not-stop-ship is a judgement rather than a formality. **BG0586** and **BG0588** together mean
the design rung's remaining bar is weaker than it reads: a run whose units were groomed before the
window, or left at `Draft`, closes clean. That is a real hole and it is the one to fix first, but
it is a hole in a rung that could not be closed AT ALL an hour ago, so it is a smaller wrong than
the one it replaced. **BG0585** is the sharpest of them - the `derived-only` detector is blind to
the very form the tooling writes - and it is ruled not-stop-ship only because nothing in this
batch relies on it: all 40 criteria here were hand-authored and independently measured red.

| Issue | Ruling | Ruled by | Date |
| --- | --- | --- | --- |
| BG0463 | deferred | authoring session (recorded for the operator) | 2026-08-16 |
| BG0567 | not-stop-ship | authoring session (recorded for the operator) | 2026-08-16 |
| BG0582 | not-stop-ship | authoring session (recorded for the operator) | 2026-08-16 |
| BG0578 | not-stop-ship | authoring session (recorded for the operator) | 2026-08-16 |
| BG0581 | not-stop-ship | authoring session (recorded for the operator) | 2026-08-16 |
| CR0509 | deferred | authoring session (recorded for the operator) | 2026-08-16 |
| CR0528 | deferred | authoring session (recorded for the operator) | 2026-08-16 |
| CR0529 | deferred | authoring session (recorded for the operator) | 2026-08-16 |
| CR0530 | deferred | authoring session (recorded for the operator) | 2026-08-16 |
| CR0531 | deferred | authoring session (recorded for the operator) | 2026-08-16 |
| CR0533 | deferred | authoring session (recorded for the operator) | 2026-08-16 |
| CR0534 | deferred | authoring session (recorded for the operator) | 2026-08-16 |
| CR0535 | deferred | authoring session (recorded for the operator) | 2026-08-16 |
| CR0536 | deferred | authoring session (recorded for the operator) | 2026-08-16 |
| CR0539 | deferred | authoring session (recorded for the operator) | 2026-08-16 |
| BG0583 | not-stop-ship | authoring session (recorded for the operator) | 2026-08-16 |
| BG0584 | not-stop-ship | authoring session (waived for this close as D0144) | 2026-08-16 |
| BG0585 | not-stop-ship | authoring session (recorded for the operator) | 2026-08-17 |
| BG0586 | not-stop-ship | authoring session (recorded for the operator) | 2026-08-17 |
| BG0587 | not-stop-ship | authoring session (recorded for the operator) | 2026-08-17 |
| BG0588 | not-stop-ship | authoring session (recorded for the operator) | 2026-08-17 |
| BG0589 | not-stop-ship | authoring session (recorded for the operator) | 2026-08-17 |
| BG0490 | deferred | operator (triage ruling, now groomed) | 2026-08-16 |
| BG0493 | deferred | operator (triage ruling, now groomed) | 2026-08-16 |

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
| US0625 | - | - | - | **UNFORECAST** (no plan-time forecast recorded; no telemetry token record) | - | - | - | - |
| US0626 | - | - | - | **UNFORECAST** (no plan-time forecast recorded; no telemetry token record) | - | - | - | - |
| US0627 | - | - | - | **UNFORECAST** (no plan-time forecast recorded; no telemetry token record) | - | - | - | - |
| US0628 | - | - | - | **UNFORECAST** (no plan-time forecast recorded; no telemetry token record) | - | - | - | - |
| US0646 | - | - | - | **UNFORECAST** (no plan-time forecast recorded; no telemetry token record) | - | - | - | - |
| US0647 | - | - | - | **UNFORECAST** (no plan-time forecast recorded; no telemetry token record) | - | - | - | - |
| US0648 | - | - | - | **UNFORECAST** (no plan-time forecast recorded; no telemetry token record) | - | - | - | - |
| US0649 | - | - | - | **UNFORECAST** (no plan-time forecast recorded; no telemetry token record) | - | - | - | - |
| US0650 | - | - | - | **UNFORECAST** (no plan-time forecast recorded; no telemetry token record) | - | - | - | - |
| US0651 | - | - | - | **UNFORECAST** (no plan-time forecast recorded; no telemetry token record) | - | - | - | - |
| BG0490 | - | - | - | **UNFORECAST** (no plan-time forecast recorded; no telemetry token record) | - | - | - | - |
| BG0493 | - | - | - | **UNFORECAST** (no plan-time forecast recorded; no telemetry token record) | - | - | - | - |
| **Batch (rated units only)** | **0** | **0** | **0** | - | **-** | | **-** | - |

**0 of 12 unit(s) measured; 0 of 12 forecast at plan time.**

Review passes, by phase - read from the two verdict ledgers:

  test-plan review: NOT IN FORCE for this run - no verdict of that phase covers any of its units, which is not the same as a run that held them and spent nothing

  code review: 24 pass(es) over 12 unit(s), 12 rejected
Unforecast: US0625, US0626, US0627, US0628, US0646, US0647, US0648, US0649, US0650, US0651, BG0490, BG0493. No plan-time forecast was recorded for them, so they are excluded too. The estimate is NOT re-derived from today's constants: a number computed at judgement time, by the model being judged, is not a prediction.
No unit in this batch is rated, so this sprint says nothing about the estimator's accuracy.

Forecast by `-`, recorded at plan time. UNFORECAST: no plan-time forecast was recorded, so there is no prediction to judge. Nothing is re-derived to fill the gap.

Ratio is estimate / actual: above 1 the plan over-forecast, below 1 it under-forecast. Nothing is re-fitted here - see VELOCITY.md for the trend across sprints, and change the constants only on evidence a human has looked at.
<!-- accuracy:end -->

* The design rung carried no forecast by design - an unsized unit is left out of the batch
  total rather than priced at a stand-in - so there is no estimate to compare against. What is
  measurable: 12 units groomed to 38 criteria, and six more transitioned as pre-work after the
  review found them already groomed.

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
| The close chain does not read the rung, so a design rung cannot be closed | BG0582 |
| The goal-review brief states an end state without knowing the rung | BG0581 |
| SC0005's scope authorised none of its own batch | fixed-in: the charter amendment of 2026-08-16 |
| Four BG0556 inventory entries stopped discriminating | fixed-in: 734c775c, admission rule tightened |
| The disclosure page and the release notes drift apart by hand | declined: filed as its own concern after this close, not repaired mid-run |

<!-- file one with: scripts/file_finding.py · check with: scripts/retro.py dispose --id RETROxxxx -->

## Close loop (gated)

`gate --require-retro RETROxxxx` (this retro's id, file form) fails until all four are true:

* [ ] this retro exists AND passes its content check - required sections, at least one real
      lesson, and every finding dispositioned (`retro.py validate --id RETROxxxx`)
* [ ] its lessons are in the project store, not just in this file (`retro.py extract --id RETROxxxx`)
* [ ] open lessons re-validated: each is closed, extended, or within its horizon (`lessons revalidate`)
* [ ] `retros/LESSONS-SUMMARY.md` regenerated from the still-valid lessons (`lessons summary`)

The next sprint reads them automatically: `sprint plan` prints the digest in the plan.

## Metrics

* Tokens: harness-tracked, not recoverable here · Duration: within one session · Goal-review
  verdicts: 2 NARROW, 1 REJECT - all three answered before the run opened

## Handoff

* [HO-0059](../handoffs/HO0059-no-open-delivery-unit-is-unplannable-every-one.md) - 12 remaining item(s): 7 copilot-tail, 5 judgement. Pick up with `sprint plan --worklist sdlc-studio/.local/handoff-worklist.txt`.
