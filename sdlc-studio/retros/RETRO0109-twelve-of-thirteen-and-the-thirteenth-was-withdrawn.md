# RETRO-0109: Twelve of thirteen, and the thirteenth was withdrawn at the close by its own review

> **Date:** 2026-08-25
> **Batch:** BG0606, BG0592, BG0611, BG0609, BG0605, BG0604, BG0610, BG0600, BG0581, BG0586, BG0587, BG0588
> **Goal:** The v5 release bar reaches zero open High: the twelve bugs open at run-open reach a terminal status carrying evidence executed against the tree AS IT STANDS AT CLOSE, or are closed by triage under a recorded reason, with no High triaged and at most four Mediums.
> **Delivered:** 12 / 12 (batch opened at 13)   **Blocked:** 1   **Verdict:** partial

## Delivered

- BG0606 - `tools/batch_plan_shape.py` reports any unit whose `## Test Plan` is not the shape `testplan derive` writes, pinning six previously-rejected rows.
- BG0592 - 18 declared mutants executed on the corpus red-criteria lane: 16 killed, 2 ruled EQUIVALENT with reasons. No new code; the code had shipped weeks earlier and only its evidence was missing.
- BG0611 - the verdict ledger's supersession join is an index built once rather than a scan repeated per row. 123s to 77s on a whole-workspace conformance run.
- BG0609 - `transition.py annotate` gained `--fields-file`; a backticked value was previously executed by the shell and its output stored in place of the text.
- BG0605 - repair state reads every row answering a rejection, so a repair split across two calls no longer reads PARTIAL twice over.
- BG0604 - the mutation-practice brief names the snapshot-and-restore obligation, not only the worktree.
- BG0610 - a fields-file scalar where a list is expected is refused, in the SHARED loader both readers use.
- BG0600 - an `unnameable` test-plan row is judged by its own contract rather than by the four rules it exists to be exempt from.
- BG0581 - the reachable end state knows its rung and the batch's types.
- BG0586 - a non-build rung must have produced something IN the run.
- BG0588 - a groomed unit short of the rung's terminal blocks the close.
- BG0587 - the grooming report and the pre-flight read ONE definition of ungroomed, for every type.

## Blocked / deferred

- **BG0607 was delivered, WITHDRAWN at the close, and DROPPED from the batch with that reason on the record; it is re-opened at High.** The other twelve reached Fixed. The close review measured the shipped fix taking whole-workspace conformance from 608/690 to 579/690, with 69 units flipping APPROVE to REJECT, on a lane that BLOCKS at `--release`. It was reverted, and a second fix direction - keying the roll-up on a recorded REPAIR, which is what the bug's own AC1 asks for - was then measured and flips the SAME 69 units, because none of those rejections carries a repair row. The defect is real and neither rule can compute it: the ledger records neither the ROUND a verdict belongs to nor the rejection an approval ANSWERS. Re-scoped to the verdict schema and carried to v5.1.
- The run's stated goal - zero open High - is therefore NOT reached, and this retro says so rather than counting the withdrawn unit as delivered.
- BG0599, BG0602 and BG0463 were CLOSED before the run rather than built: a pre-code goal review found their premises did not reproduce at HEAD. Their surviving limbs are re-filed as BG0612 and CR0557.
- Nine Medium bugs remain open and were never in this batch.

## What went well

- The pre-code goal review returned NOT-ACHIEVABLE against the 24-unit batch and was right. It re-verified all 24 premises rather than critiquing the ordering, and found SIX false - including BG0599, which was the plan's own stated enabler and had already been fixed in its load-bearing half.
- Ordering by what COMPOUNDS rather than by severity paid immediately: BG0611 first, because the run itself adds rows to the ledger it re-walks; then BG0609, because the run annotates depth fields through the verb with the shell hazard; then BG0607 and BG0605, because the run writes into two ledgers whose roll-ups were wrong.
- Treating the critic.py/transition.py units as ONE ATOMIC BLOCK - all edits, then all registrations, then all transitions - cost nothing and avoided the invalidation that cost the previous close 22 re-executions.
- The guard, not the prose, is what reported the bar - and when the bar moved back off zero at the close, `known_issues.py --bar` refused and named BG0607 before any human noticed. The release-notes claim and the corpus are pinned to each other in BOTH directions, so the retraction could not be written up as a success.

## What was hard / what stalled

- Three successive layers of the same error before the measurement landed. I told the operator for days that 20 of 21 open bugs owed an independent plan review. Not one did: the entry gate never fires for a bug because `Fixed` is not in `_IMPL_TARGETS`, and the terminal gate has no verdict check at all. TWO functions carry the identical "has no `## Test Plan`" message, and I attributed the bug refusal to the wrong one - then built two change requests and eight days of argument on top of it.
- Two mutants survived because the FIXTURE could not reach the branch. BG0586's git check is deliberately silent when git cannot answer, so a fixture with no repository behind it exercised the fail-open path and proved nothing. The mutants were not wrong; the fixtures were.
- BG0606's first cut pointed all three criteria at pytest selectors over CODE when the bug is about ARTEFACTS. All three mutants survived - a criterion whose verifier cannot reach what it claims, committed while fixing exactly that defect.
- My appetite resize never reached the config. `sprint appetite resize` applies per-run; the operator's decision was standing, and reviews/LATEST.md claimed a standing reset for four days while `.config.yaml` still read the old figure.

## Lessons

- A gate's behaviour must be read for the POPULATION you care about, not in general. Two change requests and eight days rested on the belief that bugs pay an independent plan review; measured across all 23 open bugs, none does. The two functions that refuse a missing test plan carry byte-identical messages, so the refusal a bug hits looks exactly like the refusal a story hits and comes from a different gate with different rules. D0151 records the rule; this run then broke it once more within the hour, which is the honest measure of how weak a prose rule is.
- A fixture that cannot reach the branch is a fixture that proves the fail-open path. Two mutants survived here not because the code was unguarded but because the check is deliberately silent when git cannot answer, and the fixture gave it nothing to answer with. When a guard has a documented fail-open, every test of it must first prove the guard was ASKED.
- Order a batch by what compounds over the run, not by severity. Four of this run's thirteen units repair instruments the run itself uses - the ledger it appends to, the annotate verb it calls, the roll-ups it writes into. Fixing them first made every later unit cheaper and its evidence more trustworthy; fixing them last would have meant delivering twelve units on instruments known to be wrong.
- A criterion about an ARTEFACT cannot be verified by a test over CODE. Three mutants survived BG0606's first cut for that reason, and the bug they were pinning was itself about criteria whose verifiers cannot reach what they claim.
- **Two rules agreeing is corroboration only if they are INDEPENDENT, and mine were nested.** BG0607's roll-up was keyed on the reviewer string and then on a recorded repair; both flipped the same units, and I read that agreement as proof the data was missing and the fix needed a schema change. The repair-keyed rule's unanswered set CONTAINS the reviewer-keyed one by construction - the distinguishing allowance retired two rows and changed no unit-level answer - so the agreement was guaranteed before either rule ran. An adversarial review then found the third rule in the ledger's own `Brief` column, a content hash that identifies the seat and the round together: keyed on it, the unanswered set falls from 81 units to 49, a strict superset recovering 32 and losing none. Two measurements had made me confident in a conclusion one command refutes. Before treating agreement as evidence, state what would have to be true for the two rules to disagree - if nothing could, they are one rule counted twice.
- A repair believed shipped can be withdrawn by the review that judges it, and that is the gate working - and the review that judged the WITHDRAWAL then refuted its stated reason. This one shipped, was measured against the whole corpus by an independent pass, came out, and its re-scope was wrong until a second independent pass computed the counter-example. The cost of finding it at the close rather than at the commit is one revert; the cost of not finding it is a release lane that blocks for everyone downstream, and a re-scope that would have pointed the next run at the most expensive available option.
- A pre-code review that re-verifies premises is worth more than one that critiques a plan. This one found six false premises in a 24-unit sample - two of them load-bearing for the plan itself - and cut the batch from 24 units and 89 mutants to 13 units, twelve of which closed.

## Carried lessons

The 5 that matter most for the NEXT batch, chosen now rather than ranked from the whole
store. A ranking is a fact about the past; this is a decision, re-made every retro. Bullets,
not a numbered list, and drop one for each you add (`lessons carry --displaces`).

- Read the gate's behaviour for the population you care about, from source, before proposing a change to it.
- When a guard has a documented fail-open, prove it was ASKED before believing what it reports.
- Mutate only in an isolated checkout; if you revert in place, snapshot the bytes first and restore in a `finally`.
- Register mutants AFTER the last edit to their target, and treat every unit sharing a file as one atomic block.
- A criterion is verified by something that can SEE its subject - a test over code cannot judge an artefact.

## Known issues carried

Every finding this sprint leaves OPEN, with the ruling somebody made on it. This is the one
compulsory close item the tree cannot derive: whether an open defect stops the ship is a
judgement, so it is recorded here and the sprint checklist reads it back. An open finding
with no row is reported as UNRULED, because "we carried it" and "nobody looked" must never
read the same.

Ruling is one of `stop-ship`, `not-stop-ship`, `accepted-risk`, `deferred`. A `stop-ship`
ruling HOLDS the close, which is the point of being able to make one.

**BG0607 is the one row here that needs its reason stated.** It is High, it is open, and it is ruled `deferred` rather than `stop-ship` because the thing it stops is a RELEASE TAG, not this close - and `known_issues.py --bar` already refuses that independently, naming BG0607, so the refusal does not rest on this row. What is deferred is not the decision but the BUILD: two fix directions were measured and both are wrong in the same way, and the third is a change to the verdict schema that this run has no mandate to make.

| Issue | Ruling | Ruled by | Date |
| --- | --- | --- | --- |
| BG0607 | deferred | authoring session | 2026-08-25 |
| BG0613 | not-stop-ship | authoring session | 2026-08-25 |
| BG0614 | not-stop-ship | authoring session | 2026-08-25 |
| CR0558 | deferred | authoring session | 2026-08-25 |
| BG0490 | not-stop-ship | authoring session | 2026-08-25 |
| BG0493 | not-stop-ship | authoring session | 2026-08-25 |
| BG0567 | not-stop-ship | authoring session | 2026-08-25 |
| BG0578 | not-stop-ship | authoring session | 2026-08-25 |
| BG0591 | not-stop-ship | authoring session | 2026-08-25 |
| BG0601 | not-stop-ship | authoring session | 2026-08-25 |
| BG0603 | not-stop-ship | authoring session | 2026-08-25 |
| BG0608 | not-stop-ship | authoring session | 2026-08-25 |
| BG0612 | not-stop-ship | authoring session | 2026-08-25 |
| CR0424 | deferred | authoring session | 2026-08-25 |
| CR0441 | deferred | authoring session | 2026-08-25 |
| CR0496 | deferred | authoring session | 2026-08-25 |
| CR0497 | deferred | authoring session | 2026-08-25 |
| CR0499 | deferred | authoring session | 2026-08-25 |
| CR0503 | deferred | authoring session | 2026-08-25 |
| CR0504 | deferred | authoring session | 2026-08-25 |
| CR0507 | deferred | authoring session | 2026-08-25 |
| CR0509 | deferred | authoring session | 2026-08-25 |
| CR0511 | deferred | authoring session | 2026-08-25 |
| CR0512 | deferred | authoring session | 2026-08-25 |
| CR0515 | deferred | authoring session | 2026-08-25 |
| CR0523 | deferred | authoring session | 2026-08-25 |
| CR0524 | deferred | authoring session | 2026-08-25 |
| CR0526 | deferred | authoring session | 2026-08-25 |
| CR0528 | deferred | authoring session | 2026-08-25 |
| CR0529 | deferred | authoring session | 2026-08-25 |
| CR0530 | deferred | authoring session | 2026-08-25 |
| CR0531 | deferred | authoring session | 2026-08-25 |
| CR0533 | deferred | authoring session | 2026-08-25 |
| CR0534 | deferred | authoring session | 2026-08-25 |
| CR0535 | deferred | authoring session | 2026-08-25 |
| CR0536 | deferred | authoring session | 2026-08-25 |
| CR0539 | deferred | authoring session | 2026-08-25 |
| CR0540 | deferred | authoring session | 2026-08-25 |
| CR0543 | deferred | authoring session | 2026-08-25 |
| CR0544 | deferred | authoring session | 2026-08-25 |
| CR0545 | deferred | authoring session | 2026-08-25 |
| CR0546 | deferred | authoring session | 2026-08-25 |
| CR0547 | deferred | authoring session | 2026-08-25 |
| CR0548 | deferred | authoring session | 2026-08-25 |
| CR0550 | deferred | authoring session | 2026-08-25 |
| CR0551 | deferred | authoring session | 2026-08-25 |
| CR0552 | deferred | authoring session | 2026-08-25 |
| CR0553 | deferred | authoring session | 2026-08-25 |
| CR0554 | deferred | authoring session | 2026-08-25 |
| CR0555 | deferred | authoring session | 2026-08-25 |
| CR0556 | deferred | authoring session | 2026-08-25 |
| CR0557 | deferred | authoring session | 2026-08-25 |

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

- The batch was cut from 24 units to 13 by a pre-code review, so the forecast this run was measured against is the CUT one. What the numbers say is that premise verification is the cheapest work in the run: three units closed for the cost of reading source, and six false premises were found in a 24-unit sample.

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
| Three units' premises did not reproduce at HEAD, found before any code | fixed-in: BG0599, BG0602 and BG0463 closed with their source lines recorded |
| The surviving limbs of BG0599 and BG0602 | BG0612 |
| BG0463's twenty findings need individual re-triage against HEAD | CR0557 |
| A bug gets NO independent judgement of its plan or its code - the only gate is self-reported mutant execution | CR0556 |
| The verdict ledger is re-parsed on every lookup | fixed-in: BG0611, this run |
| I claimed for days that bugs owed an independent plan review; none does | fixed-in: the record corrected at 91cd810b, and D0151 recorded as the rule I broke |
| The appetite resize never reached `.config.yaml` while LATEST.md claimed a standing reset | fixed-in: the config now carries it with its reasoning |
| `sprint_review_for` has the same last-row-wins shape BG0607 repaired in `verdict_for` | declined: raised to the delivery review to judge rather than assumed - a repair pinned on a sibling nobody measured is how this project ships half-fixes |
| The gate is over its 45s budget with the corpus scan, not the ledger, now dominant | declined: BG0608 already carries the budget-reporting half, and the scan cost is a separate measurement this run did not take |

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

- Tokens: captured by `accuracy --tokens-from-harness` at close · Duration: captured at close · Critic rejects: recorded at the delivery review
