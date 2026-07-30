# RETRO-0085: RUN-01KYPZ1G: the close found four stop-ships and the review that mattered was the one nobody ran first

> **Date:** 2026-07-30
> **Batch:** BG0402 BG0403 BG0404 BG0405 BG0407 BG0411 BG0412 BG0414 BG0416 US0452 US0453 US0454 US0455 US0456 US0457 US0458 US0459 US0460 US0461 US0462 US0463 US0464 US0465 US0476 US0477 US0478 US0484 US0485 US0486 US0560 US0561 US0562 US0563 BG0441 BG0450 BG0453 BG0446
> **Goal:** No stop-ship escapes: every defect this sprint creates is found and fixed inside the sprint by a review at each batch boundary, so the close certifies work already reviewed instead of discovering it, and no blocking defect is open at sign-off
> **Delivered:** 37 / 44   **Blocked:** 11 dropped, each with a recorded reason

## Delivered

37 units, 130 points of a 44-unit 158-point plan. Twelve bugs Fixed, ten stories Done,
fourteen at Review pending sign-off. The substance: the specs' derivable claims are now checked
against the repo rather than restated from memory; the adversarial review moved to the delivery
batch boundary; a dead-flag detector, a supersession-asymmetry detector and a derived epic index
all landed; and the whole RV0024 review residue was cleared.

## Blocked / deferred

Eleven units dropped, each with a reason recorded in the run state rather than in conversation:
seven open bugs never started (BG0401, BG0406, BG0413, BG0415, BG0359, BG0350, BG0372) and four
Draft stories the plan should never have accepted (US0564-US0567, filed as BG0449).

Eleven findings carried as tracked bugs. Six are older than this batch.

## What went well

The batch-boundary review works. Clause 1 of the goal is genuinely achieved: seven boundary
review rows across three batches, and defects now surface where the work lands rather than at the
close.

Running the SHIPPED seat briefs, rather than hand-written ones, is what produced this review round.
The claim-inventory pass they carry - and the hand-written prompts did not - is the only practice
in the ceremony aimed at prose, which is where three of the five recurring defect classes live.

Four stop-ships were found and fixed inside the close, each mutation-verified, each with a control
proving the fix had not simply broken the thing it guarded.

## What was hard / what stalled

The close cost more than it certified, and the close's own machinery said so: the outstanding set
grew 16 -> 17 and the growing-set detector reported the close was chasing a moving target rather
than converging. Filed as CR0507.

The gate that certifies the close was itself reporting a REJECTed unit as reviewed (BG0441), so
every coverage number quoted during this close before that fix was wrong.

Seven reviewers were asked whether the code was CORRECT and returned seven REJECTs, the majority
over defects older than the batch being judged. Nobody was asked the question that decides a close.

## Lessons

- EXAMPLE - replace this. A lesson is a transferable claim with the evidence that produced it, not a task: "a test that asserts a label rather than the value proves the tool named its state, not that it reached it - two of this sprint's three mutation survivors were exactly that". <!-- example -->
- **Judge an increment against the state before it, not against perfection.** Sort every finding
  into REGRESSION, new-but-better, or pre-existing, with `git log -S` deciding rather than
  judgement. Twelve findings collapsed to one regression on that test. Doing this FIRST would have
  saved most of a close: six of the twelve were older than the batch being judged.
- **A reviewer's REJECT is a verdict on a revision, not a property of the work.** Repair, then
  RE-REQUEST review. This close deadlocked because seven REJECTs were recorded, three stop-ships
  were then fixed, and nobody was asked to look again - the ordinary human loop, skipped.
- **Do not type a test selector; read it back out of the file.** Two Verify lines this session
  named classes that do not exist, both caught by `verify_ac` rather than by review. The predicate
  that would refuse them at write time already ships and no writer calls it (CR0508).

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
<!-- accuracy:end -->

- The forecast is not the interesting ratio this run. **48 unplanned artefacts against 44 planned
  units - 1.09 filed per unit planned** - is: more work was created during the run than the run
  set out to deliver. It had to be derived by hand twice (the first count of 56 wrongly swept in
  the previous run's batch), which is exactly what CR0505 / EP0192 exists to report.

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

- Critic rejects: **8** (seven closing reviewers, all REJECT; one re-review of the repaired state)
- Stop-ships found and fixed inside the close: **4** (BG0441, BG0450, BG0453, BG0446)
- Findings filed: **13** (BG0441-BG0453) plus CR0503 second attestation, CR0506, CR0507, CR0508
- Gate: **489s against a 380s budget, +54% since the 2026-07-26 baseline** - over, and reported
  with one measured number because three prior records disagreed (458s, 457s, 455s)
- Full skill suite at close: **5499 tests, OK**
