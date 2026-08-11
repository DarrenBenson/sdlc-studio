# RETRO-0101: RUN-01KZQ03V: every gate that prints a refusal performs one, and fourteen High findings close on evidence

> **Date:** 2026-08-11
> **Batch:** BG0535, BG0536, BG0542, BG0543, BG0557, US0667, US0668, US0669, BG0406, BG0457, BG0469, BG0488, BG0497, BG0522, BG0523, BG0528, BG0566, BG0569, US0670, BG0573, BG0574
> **Goal:** Every gate that prints a refusal performs one, and the acceptance criteria the README says are executable and get run do run.
> **Delivered:** 19 / 19   **Blocked:** 0

## Delivered

- Fourteen High-severity findings closed, each with an independent verdict carrying brief
  provenance, findings classified regression/new/pre-existing by execution, and a registered
  mutant per criterion. Four needed `critic repair` after a REJECT.
- The release bar became a command. `known_issues.py --bar` reads the corpus and refuses a tag
  whose claim the corpus contradicts. It has refused five times and been right every time.
- The disclosure page is GENERATED from the bug corpus and compared byte for byte, so the count
  a release states cannot drift from the findings it ships.
- The corpus verification lane can now go green and can read its own number - it tested for a
  marker the gate never prints, and its count parse could not cross a colon.
- A suite that writes into the working tree is refused at the commit boundary.

## Blocked / deferred

- US0469, US0474, US0475 - ruled OUT of scope by D0140. Checked rather than assumed: no
  changelog fragment, and one names a test file that has never existed. Planned, unbuilt, and
  carried to v5.1 as ordinary backlog rather than dropped quietly.

## What went well

- Every one of the seven gate refusals this run hit was a real defect in the author's own work.
  None would have been found by reading the diff.
- Reviewing the PLAN before the code found eleven blocking defects in the close procedure and
  four in a fix its author had called ten minutes' work.
- The bug fixed in this run reported the cause of its own close: the pre-flight now leads with
  the status blocker rather than twenty consequences of it.

## What was hard / what stalled

- Eight attempts to land one commit. Seven were gates refusing real defects; the eighth was a
  deadlock where one of this run's own findings blocked every commit until the other was fixed.
- Parallel review agents exhausted a 31G tmpfs twice, and one agent's git-touching fixtures
  destroyed another's working copy through a shared scratch directory.
- The author deleted scratch directories before checking whether a running agent was using them.

## Lessons

- A test that proves a guard works must not depend on the guard working. The test written to pin
  the fixture root guard handed it the real checkout and relied on it to refuse - so it was safe
  only while the thing it tested was correct, and it ran on the day that thing was wrong, which
  is the day it exists for. It destroyed a reviewer's checkout.
- A comparison is satisfied by agreement, INCLUDING agreement the defect produces. Three tests
  this run claimed more than they could observe: one compared two results with each other, one
  passed under the exact mutation its own message named, and one compared a set of paths so a
  write to an existing file was invisible. Assert the value, not the agreement.
- A guard narrowed to the RIGHT question can be less safe than the wrong one it replaced. The
  fixture guard asked "is this under /tmp", which refused a subdirectory for the wrong reason;
  asking "is this the repository" without the containment relation accepted it.
- A number nobody re-measures is wrong. Five stated figures were re-run this sprint and five
  were stale - the red-criteria count, the disclosed total, both suite durations, and a bug's
  own account of why its repair changed nothing.
- Reviewing the PLAN catches what code review cannot: a wrong discriminator, an exemption
  inherited unscoped, and a missing step that makes the goal unreachable rather than merely late.

## Carried lessons

The 5 that matter most for the NEXT batch, chosen now rather than ranked from the whole
store. A ranking is a fact about the past; this is a decision, re-made every retro. Bullets,
not a numbered list, and drop one for each you add (`lessons carry --displaces`).

- A mechanism that reaches no caller is inert, however well it is tested.
- Gate the CLASS, not the instance. The emptiness check that let one whole invocation surface go
  unchecked was satisfied by the other surface being present.
- Register the mutants before the transition, not after: under `report` the terminal transition
  files a bug per survivor into the disclosure the release is about to freeze.
- An enumerated list silently exempts what it forgot.
- A preview that writes is not a preview.

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
| BG0350 | not-stop-ship | Darren Benson; operator; D0136 | 2026-08-11 |
| CR0509 | not-stop-ship | Darren Benson; operator; D0136 | 2026-08-11 |
| CR0528 | not-stop-ship | Darren Benson; operator; D0136 | 2026-08-11 |
| CR0529 | not-stop-ship | Darren Benson; operator; D0136 | 2026-08-11 |
| CR0530 | not-stop-ship | Darren Benson; operator; D0136 | 2026-08-11 |
| CR0531 | not-stop-ship | Darren Benson; operator; D0136 | 2026-08-11 |
| CR0533 | not-stop-ship | Darren Benson; operator; D0136 | 2026-08-11 |
| CR0534 | not-stop-ship | Darren Benson; operator; D0136 | 2026-08-11 |
| CR0535 | not-stop-ship | Darren Benson; operator; D0136 | 2026-08-11 |
| CR0536 | not-stop-ship | Darren Benson; operator; D0136 | 2026-08-11 |
| CR0539 | not-stop-ship | Darren Benson; operator; D0136 | 2026-08-11 |
| BG0421 | not-stop-ship | Darren Benson; operator; D0136 | 2026-08-11 |
| BG0463 | not-stop-ship | Darren Benson; operator; D0136 | 2026-08-11 |
| BG0486 | not-stop-ship | Darren Benson; operator; D0136 | 2026-08-11 |
| BG0490 | not-stop-ship | Darren Benson; operator; D0136 | 2026-08-11 |
| BG0491 | not-stop-ship | Darren Benson; operator; D0136 | 2026-08-11 |
| BG0493 | not-stop-ship | Darren Benson; operator; D0136 | 2026-08-11 |
| BG0508 | not-stop-ship | Darren Benson; operator; D0136 | 2026-08-11 |
| BG0509 | not-stop-ship | Darren Benson; operator; D0136 | 2026-08-11 |
| BG0512 | not-stop-ship | Darren Benson; operator; D0136 | 2026-08-11 |
| BG0519 | not-stop-ship | Darren Benson; operator; D0136 | 2026-08-11 |
| BG0526 | not-stop-ship | Darren Benson; operator; D0136 | 2026-08-11 |
| BG0529 | not-stop-ship | Darren Benson; operator; D0136 | 2026-08-11 |
| BG0531 | not-stop-ship | Darren Benson; operator; D0136 | 2026-08-11 |
| BG0532 | not-stop-ship | Darren Benson; operator; D0136 | 2026-08-11 |
| BG0534 | not-stop-ship | Darren Benson; operator; D0136 | 2026-08-11 |
| BG0537 | not-stop-ship | Darren Benson; operator; D0136 | 2026-08-11 |
| BG0538 | not-stop-ship | Darren Benson; operator; D0136 | 2026-08-11 |
| BG0539 | not-stop-ship | Darren Benson; operator; D0136 | 2026-08-11 |
| BG0540 | not-stop-ship | Darren Benson; operator; D0136 | 2026-08-11 |
| BG0544 | not-stop-ship | Darren Benson; operator; D0136 | 2026-08-11 |
| BG0545 | not-stop-ship | Darren Benson; operator; D0136 | 2026-08-11 |
| BG0546 | not-stop-ship | Darren Benson; operator; D0136 | 2026-08-11 |
| BG0547 | not-stop-ship | Darren Benson; operator; D0136 | 2026-08-11 |
| BG0548 | not-stop-ship | Darren Benson; operator; D0136 | 2026-08-11 |
| BG0549 | not-stop-ship | Darren Benson; operator; D0136 | 2026-08-11 |
| BG0550 | not-stop-ship | Darren Benson; operator; D0136 | 2026-08-11 |
| BG0552 | not-stop-ship | Darren Benson; operator; D0136 | 2026-08-11 |
| BG0553 | not-stop-ship | Darren Benson; operator; D0136 | 2026-08-11 |
| BG0554 | not-stop-ship | Darren Benson; operator; D0136 | 2026-08-11 |
| BG0555 | not-stop-ship | Darren Benson; operator; D0136 | 2026-08-11 |
| BG0556 | not-stop-ship | Darren Benson; operator; D0136 | 2026-08-11 |
| BG0561 | not-stop-ship | Darren Benson; operator; D0136 | 2026-08-11 |
| BG0562 | not-stop-ship | Darren Benson; operator; D0136 | 2026-08-11 |
| BG0563 | not-stop-ship | Darren Benson; operator; D0136 | 2026-08-11 |
| BG0564 | not-stop-ship | Darren Benson; operator; D0136 | 2026-08-11 |
| BG0565 | not-stop-ship | Darren Benson; operator; D0136 | 2026-08-11 |
| BG0567 | not-stop-ship | Darren Benson; operator; D0136 | 2026-08-11 |
| BG0571 | not-stop-ship | Darren Benson; operator; D0136 | 2026-08-11 |
| BG0572 | not-stop-ship | Darren Benson; operator; D0136 | 2026-08-11 |

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
| BG0535 | 8 | 355,416 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| BG0536 | 3 | 133,281 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| BG0542 | 3 | 133,281 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| BG0543 | 3 | 133,281 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| BG0557 | 3 | 133,281 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| US0667 | 5 | 222,135 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| US0668 | 3 | 133,281 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| US0669 | 3 | 133,281 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| BG0406 | 5 | 230,715 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| BG0457 | 5 | 229,050 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| BG0469 | 5 | 229,050 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| BG0488 | - | - | - | **UNFORECAST** (no plan-time forecast recorded; no telemetry token record) | - | - | - | - |
| BG0497 | - | - | - | **UNFORECAST** (no plan-time forecast recorded; no telemetry token record) | - | - | - | - |
| BG0522 | - | - | - | **UNFORECAST** (no plan-time forecast recorded; no telemetry token record) | - | - | - | - |
| BG0523 | - | - | - | **UNFORECAST** (no plan-time forecast recorded; no telemetry token record) | - | - | - | - |
| BG0528 | - | - | - | **UNFORECAST** (no plan-time forecast recorded; no telemetry token record) | - | - | - | - |
| BG0566 | - | - | - | **UNFORECAST** (no plan-time forecast recorded; no telemetry token record) | - | - | - | - |
| BG0569 | - | - | - | **UNFORECAST** (no plan-time forecast recorded; no telemetry token record) | - | - | - | - |
| US0670 | - | - | - | **UNFORECAST** (no plan-time forecast recorded; no telemetry token record) | - | - | - | - |
| **Batch (rated units only)** | **0** | **0** | **0** | - | **-** | | **-** | - |

**0 of 19 unit(s) measured; 11 of 19 forecast at plan time.**

**Velocity (points/elapsed-hour): UNMEASURED.** No run-state elapsed for this sprint (an interactive sprint's wall-clock would count operator-away gaps as sprint time). Supply a real elapsed with `accuracy --elapsed-hours H` to record it - descriptive, never a target.

  secondary (points/worker-hour): UNMEASURED - no runner worker-time records (an interactive sprint has none).

Review passes, by phase - read from the two verdict ledgers:

  test-plan review: 4 pass(es) over 4 unit(s), 0 rejected

  code review: 19 pass(es) over 19 unit(s), 4 rejected

  ratio: 4.75 code-review pass(es) per test-plan pass - the claim EP0207 is judged on, as a number
Unmeasured: BG0535, BG0536, BG0542, BG0543, BG0557, US0667, US0668, US0669, BG0406, BG0457, BG0469. They are excluded from the batch ratio - an unmeasured unit is not evidence that the estimate was right.
Unforecast: BG0488, BG0497, BG0522, BG0523, BG0528, BG0566, BG0569, US0670. No plan-time forecast was recorded for them, so they are excluded too. The estimate is NOT re-derived from today's constants: a number computed at judgement time, by the model being judged, is not a prediction.
No unit in this batch is rated, so this sprint says nothing about the estimator's accuracy.

Forecast by `TOKENS_PER_POINT=25000`, recorded at plan time. OUT-OF-SAMPLE: forecast by the constants in force, on a sprint they were not fitted to. This is the only kind of row that tells you anything.

Ratio is estimate / actual: above 1 the plan over-forecast, below 1 it under-forecast. Nothing is re-fitted here - see VELOCITY.md for the trend across sprints, and change the constants only on evidence a human has looked at.
<!-- accuracy:end -->

- The batch grew from 8 planned units to 19, so the plan-time forecast measures a run that did
  not happen. The creep is recorded rather than explained away: ten High findings were added to
  the batch under D0136 because the tag bar demanded them, and four more findings were raised by
  the run's own reviews and fixed inside it.

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
| The repaired spec-agreement guards match word patterns, so a passage stating the opposite rule passes | BG0571 |
| The repo-writes lane attributes any concurrent edit to the test run | BG0572 |
| Running the suite from inside scripts/ destroys the checkout | fixed-in: 7c544d9d |
| A --dry-run takes the allocation lock on the target repository | fixed-in: 7c544d9d |
| plan_review has no adoption cutoff, so it cannot be turned on by a project with history | CR0543 |
| Nothing reviews a repair's approach or a procedure's plan before it is executed | CR0544 |
| The corpus lane could not go green and could not read its own number | fixed-in: ae95ce04 |

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

- Tokens: captured from the harness by the close · Duration: one interactive session · Critic rejects: 6 (BG0406 twice, BG0497, BG0573, BG0574, and the batch pass that rejected 4 of 8)
