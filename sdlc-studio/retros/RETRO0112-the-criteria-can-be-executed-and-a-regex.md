# RETRO-0112: the criteria can be executed, and a regex that rewrote 57 files to fix three spans

> **Date:** 2026-09-02
> **Batch:** BG0635, BG0636, BG0628, BG0631
> **Goal:** A unit's acceptance criteria can be EXECUTED, and the instruments that judge them report one number each.
> **Delivered:** 4 / 4   **Blocked:** 0   **Verdict:** achieved

## Delivered

- BG0636 - `file_finding.py file`, the command the doctrine names for filing every finding, had `--ac` and nothing to pair with it, so there was NO route to an executable acceptance criterion for a bug. `artifact.py new` appears to offer the model and does not: `--verify` is story-only and is silently dropped. `unit_is_ungroomed` tested three shapes and executability was not among them. `sprint plan` now reports 9 ungroomed over the same corpus that read 0 that morning.
- BG0635 - the close counted the lanes its own pre-flight calls advisory, so `loop_termination`'s converged branch was unreachable and the cap stopped a run no value could have satisfied. `review.max_rounds` is REMOVED rather than set: one key, two consumers, different defaults. D0177's interim authorisation expired on this commit exactly as written.
- BG0628 - the conformance figure was a fact about the tree rather than the corpus. A complete checkout and a `sdlc-studio/`-only copy now both read 731/814; the partial tree names its 496 unevaluable units instead of scoring them as debt.
- BG0631 - a repair row was joined to its rejection by date alone, so a delivery repair discharged a plan-review rejection carrying the same finding text. Legacy rows are attributed on their own closures where the date is ambiguous, and the 13 that cannot be placed are REPORTED.

## Blocked / deferred

- Nothing was blocked. All four reached Fixed and the release bar returned to MET.
- BG0632, BG0634 and BG0639 closed by TRIAGE rather than code, each on a re-run against HEAD.
- US0674 moved the other way and is reported rather than repaired: its legacy repair rows answer their rejection in substance but not mechanically, and attributing them anyway is the guessing BG0631 AC4 exists to refuse.

## What went well

- The plan review paid for itself twice over before a line was written. It found that all 25 criteria of the originally proposed 7-unit batch were unexecutable, and that BG0636's own fix would have added a fourth `_AC_MISS` reason to a bare dict subscript - a `KeyError` taking down `plan` and `breakdown` for every batch holding such a unit, in a file the unit had not declared.
- Three of the seven originally proposed units did not reproduce. Re-running each premise against HEAD before coding is what caught it; two would have been coded against symptoms nobody had re-measured.
- Control rows caught an over-correction no target row could. My predicate read `b.verify` where `ACBlock` carries `verifier`, so it refused every unit - and a predicate that refuses everything satisfies every target assertion in the suite.

## What was hard / what stalled

- **A regex run to fix three code spans rewrote 57 files.** MD038 flagged three spans in BG0636. Instead of fixing those three, I wrote a pattern over every code span in `sdlc-studio/bugs/*.md` and `changelog.d/*.md` and modified 39 bug artefacts and 18 changelog fragments from earlier runs. It was caught immediately and every file was restorable, because all 45 were committed. That is git saving it, not judgement.
- **The fix for that was ALSO too wide.** Restoring the 45 files from HEAD reverted `bugs/_index.md`, which carried this batch's own rows - so the next commit was blocked on 17 rows of index drift. The same error twice in ten minutes: a broad action where a narrow one was called for.
- **`npm run lint` passed while the commit hook refused.** The strict markdown rules over `bugs/` run in the hook, not in `lint`, so a locally green tree said nothing about the gate. Worth knowing before trusting a lint result as a commit predictor.
- **One criterion was amended mid-delivery.** BG0636 AC2 required the FILER to refuse an unverifiable criterion. Implementing it revealed a blast radius nobody had measured - `acs` is authored across ten test modules here and by every consuming project's scripts - so the refusal moved to the planner. Recorded as D0178 rather than quietly softened, because a criterion changed during its own delivery is exactly what a review would otherwise catch as moved goalposts.
- **The delivery review REJECTED all four units, and found a regression nothing else would have caught.** Appending two ledger columns at once broke `_read_rows`' short-by-one bound, so every six-cell legacy repair row became unreadable: `repairs_for` returned nothing and the test-plan gate began refusing units whose repairs were on record. This repository had migrated its own header and never saw it; every consuming project would have, on upgrade, with no migration to run. The lesson is in the fixture: a schema-widening test built on the shape THIS repo holds cannot see the shape everyone else holds.
- **Two of my tests did not exercise the claims they were written for.** BG0636 AC3 drove `breakdown`, which exits 0, where the criterion names the `plan` REFUSAL - so deleting the plan gate left the test green while `plan` printed a full wave at rc=0. AC7 performed no set comparison at all though its criterion makes comparing sets the point, and a mutant refusing 391 units instead of 92 passed it. Both are the L-0383 shape one level up: not a library test where a CLI claim was made, but the WRONG command, and a read-only one.
- **BG0631 AC3 was stamped complete with half its text unbuilt.** The criterion says the row names the phase AND the rejection, and says the ledger carries neither; only the phase was added, and the verifier asserted only that half. A criterion that enumerates two things needs an oracle for both, or the half nobody asserts is the half nobody builds.
- **Four prose surfaces contradicted the code they described.** Three still said the filer REFUSES after D0178 made it report; a code comment claimed the closure fallback had rescued US0674, which reads `none` either way - and the changelog said so correctly, so two surfaces in one diff disagreed and the code was the false one.
- **My own hand-rolled census was wrong and I put it in a criterion.** I reported "15 bugs, 53 criteria" from a script written for the occasion; the shipped `corpus-scan` reports 51 carrying no verifier and 61 unreadable. AGENTS.md names hand-rolled censuses as one of this repo's five recorded failure modes.

## Lessons

- **Narrow the licence, not the pattern.** A lint error in three code spans was fixed by a regex over every code span in two directories, rewriting 57 files to change three. The same session had already recorded that lesson from BG0623, where three review rounds each widened the licence to overwrite and each destroyed the next shape along. Knowing the lesson did not prevent it; the tell is the same both times - reaching for a rule that matches a CLASS when the job names specific INSTANCES. When the target is enumerable, enumerate it.
- **A tool that cannot author its evidence produces units nobody can check.** `file_finding.py` could write an acceptance criterion but not its verifier, and nothing downstream noticed: grooming asked whether a criterion was WRITTEN, never whether it could be CHECKED, so 51 bug files reached a terminal status on criteria that were never tests. A gate that inspects the shape of work rather than its checkability certifies the wrong thing.
- **A schema-widening test built on the shape YOUR repo holds cannot see the shape everyone else holds.** Two ledger columns were appended at once, and the reader tolerated a row short by exactly one - so every pre-column ledger stopped parsing and a gate began refusing units whose evidence was on record. This repository had migrated its own header, so its tests were all written on the migrated shape and every one of them passed. The failure is invisible from inside the repo that did the migration, and it lands on every consumer at upgrade. Fixture the OLDEST supported shape, not the current one.
- **The vacuous case is where a per-item rule fails, and it is the largest population.** "Every criterion carries a verifier" is TRUE over an empty list, and 61 bug files parse to no criteria at all - more than the 51 the rule was written for. Any rule quantified over a collection needs an explicit answer for the empty collection, or its biggest sub-population passes without ever being wrong.

## Carried lessons

The 5 that matter most for the NEXT batch, chosen now rather than ranked from the whole
store. A ranking is a fact about the past; this is a decision, re-made every retro. Bullets,
not a numbered list, and drop one for each you add (`lessons carry --displaces`).

- A test that asserts a label rather than the value proves the tool named its state, not that it reached it.
- A mechanism that reaches no caller is inert, however well it is tested.
- A repair breaks its neighbours, and a rename is cross-unit coupling.
- An enumerated list silently exempts what it forgot.
- Verify the premise before building on it - three of seven proposed units did not reproduce.

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
| BG0567 | not-stop-ship | sdlc-studio (agent) | 2026-09-02 |
| BG0591 | not-stop-ship | sdlc-studio (agent) | 2026-09-02 |
| BG0601 | not-stop-ship | sdlc-studio (agent) | 2026-09-02 |
| BG0603 | not-stop-ship | sdlc-studio (agent) | 2026-09-02 |
| BG0608 | not-stop-ship | sdlc-studio (agent) | 2026-09-02 |
| BG0612 | not-stop-ship | sdlc-studio (agent) | 2026-09-02 |
| BG0614 | not-stop-ship | sdlc-studio (agent) | 2026-09-02 |
| BG0627 | not-stop-ship | sdlc-studio (agent) | 2026-09-02 |
| BG0630 | not-stop-ship | sdlc-studio (agent) | 2026-09-02 |
| BG0633 | not-stop-ship | sdlc-studio (agent) | 2026-09-02 |
| BG0637 | not-stop-ship | sdlc-studio (agent) | 2026-09-02 |
| BG0638 | not-stop-ship | sdlc-studio (agent) | 2026-09-02 |
| CR0509 | not-stop-ship | sdlc-studio (agent) | 2026-09-02 |
| CR0528 | not-stop-ship | sdlc-studio (agent) | 2026-09-02 |
| CR0529 | not-stop-ship | sdlc-studio (agent) | 2026-09-02 |
| CR0530 | not-stop-ship | sdlc-studio (agent) | 2026-09-02 |
| CR0531 | not-stop-ship | sdlc-studio (agent) | 2026-09-02 |
| CR0533 | not-stop-ship | sdlc-studio (agent) | 2026-09-02 |
| CR0534 | not-stop-ship | sdlc-studio (agent) | 2026-09-02 |
| CR0535 | not-stop-ship | sdlc-studio (agent) | 2026-09-02 |
| CR0536 | not-stop-ship | sdlc-studio (agent) | 2026-09-02 |
| CR0539 | not-stop-ship | sdlc-studio (agent) | 2026-09-02 |
| CR0546 | not-stop-ship | sdlc-studio (agent) | 2026-09-02 |
| CR0547 | not-stop-ship | sdlc-studio (agent) | 2026-09-02 |
| CR0548 | not-stop-ship | sdlc-studio (agent) | 2026-09-02 |
| CR0550 | not-stop-ship | sdlc-studio (agent) | 2026-09-02 |
| CR0551 | not-stop-ship | sdlc-studio (agent) | 2026-09-02 |
| CR0552 | not-stop-ship | sdlc-studio (agent) | 2026-09-02 |
| CR0553 | not-stop-ship | sdlc-studio (agent) | 2026-09-02 |
| CR0554 | not-stop-ship | sdlc-studio (agent) | 2026-09-02 |
| CR0555 | not-stop-ship | sdlc-studio (agent) | 2026-09-02 |
| CR0556 | not-stop-ship | sdlc-studio (agent) | 2026-09-02 |
| CR0557 | not-stop-ship | sdlc-studio (agent) | 2026-09-02 |
| CR0558 | not-stop-ship | sdlc-studio (agent) | 2026-09-02 |
| CR0559 | not-stop-ship | sdlc-studio (agent) | 2026-09-02 |
| CR0560 | not-stop-ship | sdlc-studio (agent) | 2026-09-02 |
| CR0561 | not-stop-ship | sdlc-studio (agent) | 2026-09-02 |
| CR0562 | not-stop-ship | sdlc-studio (agent) | 2026-09-02 |
| CR0511 | not-stop-ship | sdlc-studio (agent) | 2026-09-02 |
| US0674 | not-stop-ship | sdlc-studio (agent) | 2026-09-02 |

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
| BG0635 | 3 | 113,661 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| BG0636 | 5 | 189,435 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| BG0628 | 3 | 113,661 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| BG0631 | 5 | 189,435 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| **Batch (rated units only)** | **0** | **0** | **0** | - | **-** | | **-** | - |

**0 of 4 unit(s) measured; 4 of 4 forecast at plan time.**

**Velocity (points/elapsed-hour): UNMEASURED.** No run-state elapsed for this sprint (an interactive sprint's wall-clock would count operator-away gaps as sprint time). Supply a real elapsed with `accuracy --elapsed-hours H` to record it - descriptive, never a target.

  secondary (points/worker-hour): UNMEASURED - no runner worker-time records (an interactive sprint has none).

Review passes, by phase - read from the two verdict ledgers:

  test-plan review: NOT IN FORCE for this run - no verdict of that phase covers any of its units, which is not the same as a run that held them and spent nothing

  code review: 4 pass(es) over 4 unit(s), 4 rejected
Unmeasured: BG0635, BG0636, BG0628, BG0631. They are excluded from the batch ratio - an unmeasured unit is not evidence that the estimate was right.
No unit in this batch is rated, so this sprint says nothing about the estimator's accuracy.

Forecast by `TOKENS_PER_POINT=25000`, recorded at plan time. OUT-OF-SAMPLE: forecast by the constants in force, on a sprint they were not fitted to. This is the only kind of row that tells you anything.

Ratio is estimate / actual: above 1 the plan over-forecast, below 1 it under-forecast. Nothing is re-fitted here - see VELOCITY.md for the trend across sprints, and change the constants only on evidence a human has looked at.
<!-- accuracy:end -->

- Four units, 16 points, against a batch first proposed at seven units and 23 points and REFUSED at plan review. The refusal is the cheapest thing that happened all run: it cost three seat reviews and saved coding four units whose premises had expired and twenty-five criteria that could not be executed.

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
| A regex run to fix three code spans rewrote 57 files; the restore was also too wide and reverted this batch's index rows | fixed-in: 51585963 - both caught and reverted in session, and recorded as this retro's first lesson |
| `_clean` escapes underscores inside code spans, corrupting 655 identifiers across the three review ledgers | BG0637 |
| Five sprint-checklist rows state conclusions they never established; `_ck_known_issues` fails open where its sibling reports the same blindness as UNANSWERED | BG0638 |
| The retro index heads its second column Sprint where every sibling heads it Title, so retitle leaves a stale description beside a rewritten link | CR0511 |
| Nothing ticks a delivered unit's acceptance criteria, so a compulsory close row can only be answered by hand | CR0562 |
| `review.max_rounds` is a conflated key: sprint.py reads it as a close-attempt cap defaulting to 4, critic.py as a review-round ceiling defaulting to 3 | declined: removing the key gives each consumer its own default and is the shipped behaviour again; splitting it is a separate decision nobody needs yet |
| US0674's legacy repair rows answer their rejection in substance but not mechanically, so it reads non-conformant | declined: attributing them anyway is the guessing BG0631 AC4 exists to refuse - reported in the changelog instead |

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

- Tokens: captured at close · Duration: 2026-09-02 to 2026-09-03 · Plan reviews: 3 rounds, 9 seat verdicts, the first batch REFUSED outright · Delivery reviews: 2 rounds, 4 of 4 units REJECTED, every finding answered by a recorded repair · Mutants: 29 executed, 29 killed, `not-run 0` on all four

## Handoff

- [HO-0066](../handoffs/HO0066-a-unit-s-acceptance-criteria-can-be-executed.md) - 4 remaining item(s): 0 copilot-tail, 4 judgement. Pick up with `sprint plan --worklist sdlc-studio/.local/handoff-worklist.txt`.
