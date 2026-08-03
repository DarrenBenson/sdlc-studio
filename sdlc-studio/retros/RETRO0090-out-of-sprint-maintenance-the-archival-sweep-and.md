# RETRO-0090: Out-of-sprint maintenance: the archival sweep, and the guards that refused it

> **Date:** 2026-08-03
> **Batch:** BG0504, BG0503, BG0505
> **Goal:** clear the five index-archival advisories, file the reconcile gap the backlog analysis found, and repair both findings it raised
> **Delivered:** 3 / 3   **Blocked:** 0
> **Velocity-override:** no sprint ran, so there is no plan-time forecast to measure an actual against. Three units repaired inside a maintenance task carry no appetite, no batch and no rate this record could re-measure, and writing a row would put a number into the tokens-per-point series that no plan produced.

## Delivered

- `BG0504` - the two repo guards that read `_index.md` with a bare `read_text` now read it
  unioned with its `archive/**` sub-indexes, so archiving no longer turns them red. Shipped in
  `fa7cd067` with `changelog.d/BG0504.md`.
- `BG0503` - `reconcile detect` gained an `epic-status-stale` kind: an epic still live over a
  breakdown whose every declared unit is terminal. Detect-only on purpose, because closing an
  epic is a transition and `transition.py set` is where its gates live. Shipped in `c215541c`.
- `BG0505` - `check_spec_claims.py` compares a bare filename against the diff's basenames rather
  than its paths, so the commonest way to name a Python test no longer guarantees a claim-drift
  finding. Shipped in `c215541c`.

The last two were filed by this same maintenance task and carried as not-stop-ship; the operator
asked for them next, so they were repaired in the thread that raised them rather than planned into
a sprint. That is why they appear both in **Actions raised** and in **Delivered**.

The occasion was not a sprint. A backlog analysis over the 164 open artefacts reported five
indexes between 6x and 15x `indexes.archive_after`, and the operator asked for the sweep. It ran:
1,153 terminal rows moved to `archive/v5.0.0/` (472 story, 271 cr, 178 bug, 177 epic, 55 rfc),
all five advisories cleared, `drift_items=0`, census unchanged.

## Blocked / deferred

Nothing was blocked. Two findings were filed rather than fixed - see **Known issues carried**.

## What went well

- **The archival machinery was correct throughout.** `parse_index` already unioned the archive
  back in, `epic_index_derivable_drift`, `epic_index_uncorroborated_advisory` and `reconcile
  detect` all returned correct results over the archived tree, and the census never moved. Only
  the tests' own reading of the corpus was stale, which is the cheapest place for the defect to
  have been.
- **The suite-verdict guard refused a claim it could not corroborate.** The commit message said
  the suite was green; the recorded verdict was from an earlier commit, and the commit-msg lane
  said so rather than believing the prose. That lane was written because a red suite once read as
  green through a pipe, and it did its job on an author who had in fact run the suite.

## What was hard / what stalled

- **The failure gave no hint of its cause.** Seven tests failed naming the epic index and the
  supersession record. Nothing in the output connected them to the archival command run minutes
  earlier, and an agent reading only the failures would have concluded the index was corrupt and
  repaired the wrong thing. The diagnosis came from having just run the sweep, not from the
  message.
- **A false positive in an advisory lane cost a diagnosis.** claim-drift reported `BG0504`'s AC3
  as ticked over a file the diff changed by 76 lines. Confirming it was wrong meant reading
  `check_spec_claims.py` rather than trusting the lane - `BG0505`.
- **Filing a finding needed the artefact edited afterwards.** `transition -> Fixed` refuses
  without a parseable `Verification depth`, and `file_finding.py` writes no such field, so the
  bug had to be hand-edited between filing and transition. Small, and repeated once per finding.

## Lessons

- **A guard that reads the live index treats "what nobody has archived yet" as the corpus.** Both
  failing guards asserted floors - `> 150` rows, `> 100` epics - that exist to prove the sweep is
  not silently matching nothing. Calibrated against an unarchived snapshot, the floor tracks the
  snapshot rather than the corpus, so the guard reddens on a maintenance step instead of on a
  defect. The population, not the number, is what needed fixing.
- **An operation the tooling advises on every run, and that nobody can commit, accumulates
  silently and is invisible in the advisory itself.** Five indexes reached 6-15x their threshold
  while `reconcile detect` printed the remedy every time. The advisory reported the state
  correctly and could not report that taking its own advice was blocked, which is why the debt
  grew rather than being paid. Exercise the remedy an advisory prints, not just the detector that
  prints it.
- **A cascade that ticks a checkbox is not a status cascade.** `_cascade_epic` ticks the story's
  line in its parent's Story Breakdown and returns; it never touches the parent's Status. Fifteen
  of thirty open epics have every child Done and every box ticked and still read Draft, and
  `reconcile detect` reports `drift_items=0` over all of them. The direction that masks unfinished
  work was detected; the direction that masks finished work was not, so a delivery backlog can be
  overstated by half and nothing says so - `BG0503`, now the `epic-status-stale` kind. Clearing it
  showed the overstatement was not confined to the epic layer: closing the fifteen made 29
  requests derivable, and Discovery fell 60 to 31, Delivery 106 to 89. A roll-up that is not
  derived is wrong at every layer above it, not only at the one that stopped deriving.

## Carried lessons

The 5 that matter most for the NEXT batch, chosen now rather than ranked from the whole
store. A ranking is a fact about the past; this is a decision, re-made every retro. Bullets,
not a numbered list, and drop one for each you add (`lessons carry --displaces`).

- A review exists when the ledger says so, not when it happened - RUN-01KYZKY5 lost fifteen units'
  worth of judgement to a `critic record` nobody ran.
- A mutation-killed test proves the test can fail, not that production takes that path. Drive the
  shipped entry point, not the library.
- A repair made during a close weakens the test beside it. Nothing is fixed during a close.
- A mechanism that reaches no caller is inert, however well it is tested.
- An enumerated list silently exempts whatever it forgot.

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

**Nothing is carried.** `BG0503` and `BG0505` were ruled `not-stop-ship` here when they were
filed - the epics were miscounted rather than broken, and claim-drift is advisory and cannot
fail a commit. The operator then asked for both, so they were repaired in `c215541c` instead of
being carried, and the rows were removed rather than left contradicting the Delivered list. The
ruling is recorded because a finding that was looked at and deferred must never read the same as
one nobody looked at, even after the deferral is overtaken.

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

- **Not applicable.** No sprint opened, so no run baseline was stamped and no unit carries a
  plan-time forecast. All three units were sized after the fact, which is a record of the job
  rather than a prediction anything can be scored against. The velocity override above states the
  same fact in the form the close reads.

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

| Finding | Disposition |
| --- | --- |
| Fifteen Draft epics have every child terminal and no detector says so | BG0503, fixed-in: c215541c |
| Two repo guards read the live index as the whole corpus, so archiving reddens them | fixed-in: fa7cd067 |
| claim-drift matches a bare filename against full repo paths, a guaranteed false positive on any `unittest -p` Verify line | BG0505, fixed-in: c215541c |
| `file_finding.py` writes no `Verification depth`, so every filed bug must be hand-edited before `transition -> Fixed` will accept it | declined: one field edit per finding, and inventing a depth at filing time would record a verification nobody performed - the refusal is asking the right question at the right moment |

<!-- file one with: scripts/file_finding.py · check with: scripts/retro.py dispose --id RETROxxxx -->

## Close loop (gated)

`gate --require-retro RETRO0090` (this retro's id, file form) fails until all four are true:

- [x] this retro exists AND passes its content check - required sections, at least one real
      lesson, and every finding dispositioned (`retro.py validate --id RETRO0090`)
- [x] its lessons are in the project store, not just in this file (`retro.py extract --id RETRO0090`)
- [x] open lessons re-validated: each is closed, extended, or within its horizon (`lessons revalidate`)
- [x] `retros/LESSONS-SUMMARY.md` regenerated from the still-valid lessons (`lessons summary`)

The next sprint reads them automatically: `sprint plan` prints the digest in the plan.

## Metrics

- Tokens: not-attributable (no run baseline - this was maintenance, not a sprint) · Duration: one session · Critic rejects: none - none of the three units carries an independent review, which is recorded here rather than implied by its absence
