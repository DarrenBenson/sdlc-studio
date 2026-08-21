# RETRO-0107: the marginal yield of a review round is not flat, and this run measured where it falls off

> **Date:** 2026-08-21
> **Batch:** BG0593, BG0594, BG0595, BG0596, BG0597, BG0598
> **Goal:** Every instrument this run touches reports only a verdict its own recorded evidence supports, and refuses rather than softens when the evidence is not there
> **Delivered:** 6 / 6   **Blocked:** 0

## Delivered

- BG0593 - `close --dry-run` previewed against a scratch with no git, so every git-reading row degraded to a softer verdict than the close it previews. The scratch is now a pure copy with no links out of it and a separate read root travels beside it, reaching only the steps whose signature accepts one. Measured: the pre-flight reports 22 refusals and ZERO unevaluated steps, where the tick row previously read `diff unreadable`.
- BG0594 - the gate budget compared one scalar against one ceiling, so a slower gate over fewer tests read as an improvement. It now reports a per-test rate beside the total and judges against a declared `rate_seconds_per_test`. Live at 0.116 s/test against a 0.152 ceiling.
- BG0595 - the commit-msg hook test was not hermetic: it depended on caller-identity signals the suite leaves set, so the message-absent early exit was never exercised as a refusal.
- BG0596 - `_testplan_rows` collapsed multiple rows per criterion into one, so a criterion with three planned mutants registered as one. `--from-plan` now reports 18 planned mutants across 15 criteria on BG0592 where it read 15, and refuses because three rows were never executed.
- BG0597 - `testplan derive` emitted one row per criterion block and silently dropped orphan rows; it now refuses them by name.
- BG0598 - `sprint.py` read review rounds from one ledger where two exist, so a unit whose only REJECT sat in the batch ledger read as unreviewed and was priced as built.

## Blocked / deferred

- Reviewer-of-record sign-off is the operator's. `critic signoff` refuses a principal the authoring session controls, which is the gate working.
- BG0601, BG0602, BG0603 filed as residue from the delivery review rather than fixed here: a class sweep truncating each probe to two elements (a demonstrated bypass, not a hypothesis), a close checklist deriving its roster from an `_ck_` name prefix, and `lint_stacked_verifiers` applied at Draft and Ready but not at Open - which is the status a bug occupies for its entire delivery.
- CR0549 and CR0550 filed against the review machinery itself, on the operator's ruling about this run's cost.

## What went well

- The sprint goal was met and is demonstrable rather than asserted. Every headline above is a number taken from the shipped entry point after the change, with the reading it replaced beside it.
- Round 6 ruled all five earlier rounds CLOSED with execution behind each, and NONE moved. That is the first round in this run without a relocated defect, after three rounds that each found a repair had shifted its defect rather than fixed it.
- 33 of 33 nameable mutants executed and killed by their own named verifier, each as a single test node with `__pycache__` purged, the target hash checked changed then byte-identical after. Three rows are declared `unnameable` and disclosed as such.
- The reviewers worked in isolated git worktrees and left the shared tree byte-clean. An earlier run had a reviewer destroy uncommitted work; that did not recur.
- The gates refused correctly and repeatedly: the workspace census caught three stacked `Verify:` lines on one criterion, the style guard caught ten internal bug ids in shipped `scripts/`, `repo-writes` held, and `run-suite --check` refused a stale verdict.

## What was hard / what stalled

- Eleven independent review rounds for six units - five on the test plan, six on the delivery. The run cost 11,034,109 main-thread tokens for 21 points: 525,434 per point against a 44,427 forecast, and against a corpus history whose worst previous row is 353,810. Subagent tokens are not counted in that figure and the review rounds ran as subagents, so it understates the position.
- The marginal yield of those rounds was NOT flat, and this is the run's most useful measurement. Delivery round 1 caught a defect that would have shipped - BG0593's entire production change deletable with all 916 tests in its file green, because the tests rebuilt the mechanism in a private helper. Rounds 2 to 5 caught only defects in the evidence apparatus, most of them manufactured by the registration ledger rather than found in the code.
- The mutation ledger accumulated DUPLICATE live rows. Each retract-and-re-register during rounds 3 and 4 left the superseded row live beside its replacement; seven criteria carried two each, and `plan_execution` joins on `(criterion, row)` and takes whichever entry is iterated last. No gate saw it.
- Three suite verdicts went stale because the tree was edited after the verdict was recorded. The guard caught it every time; the waste was mine.
- The delivery-round verdicts were never written to the ledger until the close demanded them. Five adversarial passes with no recorded row is the RETRO0089 cause, occurring in a run that had read the lesson.

## Lessons

- A retract-and-re-register cycle leaves the superseded row LIVE unless something withdraws it, and a join keyed on `(criterion, row)` then silently resolves to whichever row is iterated last. Withdraw before re-registering, then audit for duplicate live rows - the audit is four lines and nothing else in the toolchain performs it.
- Re-registering against a file edited since the first registration DISCARDS the earlier verdicts, and that is correct. BG0594's four rows went to zero for exactly this reason and had to be re-executed against the current bytes. Register after the last edit, or budget for re-running.
- A changelog fragment written at the first commit describes the design that existed THEN. A redesign must rewrite the fragment, not only the code: BG0593's shipped for three commits describing the symlink mechanism its own AC3 forbids by name, and was caught only when a reviewer applied the fragment's own words as a mutant and watched the unit's test kill it.
- Ceremony scaled by FILE size is not ceremony scaled by risk. `route.estimate` takes 0.40 of its weight from a complexity read over every function in every declared file, so a two-line change to a large module inherits that module's worst function. Measured over 603 bugs: 87% tier `full`, `code` and `risk` both saturated for 48%, and half the corpus inside a six-point score spread. A gate with that little dynamic range is a constant wearing the appearance of a gate.
- Marginal review yield decays, and a round cap should be set from that rather than from batch size. D0132 raised the cap to 6 reasoning that bigger batches take more rounds; this run shows the later rounds converging on the evidence apparatus rather than on the code.

## Carried lessons

The 5 that matter most for the NEXT batch, chosen now rather than ranked from the whole
store. A ranking is a fact about the past; this is a decision, re-made every retro. Bullets,
not a numbered list, and drop one for each you add (`lessons carry --displaces`).

- Round 1 of a delivery review catches shipped defects; later rounds converge on the evidence apparatus. Cap the rounds and file the residue.
- A retract-and-re-register leaves the superseded mutation row LIVE - withdraw first, then audit for duplicates, because no gate does.
- Register mutants AFTER the last edit, or re-registering discards the earlier verdicts and you re-execute.
- A redesign must rewrite the changelog fragment, not only the code - the fragment describes the design that existed when it was written.
- Ceremony scaled by FILE size is not ceremony scaled by risk.

## Known issues carried

Every finding this sprint leaves OPEN, with the ruling somebody made on it. This is the one
compulsory close item the tree cannot derive: whether an open defect stops the ship is a
judgement, so it is recorded here and the sprint checklist reads it back. An open finding
with no row is reported as UNRULED, because "we carried it" and "nobody looked" must never
read the same.

Ruling is one of `stop-ship`, `not-stop-ship`, `accepted-risk`, `deferred`. A `stop-ship`
ruling HOLDS the close, which is the point of being able to make one.

**Eight of the rows below are HIGH severity and are ruled `deferred`, not fixed.** BG0586,
BG0588 and BG0592 are design-rung and corpus-metric defects carried from RUN-01M05A5M; CR0509,
CR0533, CR0534, CR0535, CR0536, CR0546, CR0547 and CR0548 are requests rather than defects in
delivered behaviour. None was touched by this run and none is a regression from it. They are
deferred rather than marked not-stop-ship because that is the honest word: they are real, they
are open, and they are waiting on capacity rather than on a judgement that they do not matter.
CR0547 and CR0548 in particular would have caught this run's worst findings - a revert-check
gate, and a `Verification depth` derived from the ledger instead of authored by hand.

| Issue | Ruling | Ruled by | Date |
| --- | --- | --- | --- |
| BG0463 | deferred | authoring session | 2026-08-21 |
| BG0567 | not-stop-ship | authoring session | 2026-08-21 |
| BG0586 | deferred | authoring session | 2026-08-21 |
| BG0587 | not-stop-ship | authoring session | 2026-08-21 |
| BG0588 | deferred | authoring session | 2026-08-21 |
| BG0591 | not-stop-ship | authoring session | 2026-08-21 |
| BG0592 | deferred | authoring session | 2026-08-21 |
| BG0599 | not-stop-ship | authoring session | 2026-08-21 |
| BG0600 | not-stop-ship | authoring session | 2026-08-21 |
| CR0509 | deferred | authoring session | 2026-08-21 |
| CR0528 | deferred | authoring session | 2026-08-21 |
| CR0529 | deferred | authoring session | 2026-08-21 |
| CR0530 | deferred | authoring session | 2026-08-21 |
| CR0531 | deferred | authoring session | 2026-08-21 |
| CR0533 | deferred | authoring session | 2026-08-21 |
| CR0534 | deferred | authoring session | 2026-08-21 |
| CR0535 | deferred | authoring session | 2026-08-21 |
| CR0536 | deferred | authoring session | 2026-08-21 |
| CR0539 | deferred | authoring session | 2026-08-21 |
| CR0546 | deferred | authoring session | 2026-08-21 |
| CR0547 | deferred | authoring session | 2026-08-21 |
| CR0548 | deferred | authoring session | 2026-08-21 |
| BG0601 | not-stop-ship | authoring session | 2026-08-21 |
| BG0602 | not-stop-ship | authoring session | 2026-08-21 |
| BG0603 | not-stop-ship | authoring session | 2026-08-21 |
| CR0549 | not-stop-ship | authoring session | 2026-08-21 |
| CR0550 | not-stop-ship | authoring session | 2026-08-21 |

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
| BG0593 | 3 | 133,281 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| BG0594 | 2 | 88,854 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| BG0595 | 2 | 88,854 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| BG0596 | 2 | 88,854 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| BG0597 | 3 | 133,281 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| BG0598 | 2 | 88,854 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| **Batch (rated units only)** | **0** | **0** | **0** | - | **-** | | **-** | - |

**0 of 6 unit(s) measured; 6 of 6 forecast at plan time.**

**Velocity (points/elapsed-hour): UNMEASURED.** No run-state elapsed for this sprint (an interactive sprint's wall-clock would count operator-away gaps as sprint time). Supply a real elapsed with `accuracy --elapsed-hours H` to record it - descriptive, never a target.

  secondary (points/worker-hour): UNMEASURED - no runner worker-time records (an interactive sprint has none).

Review passes, by phase - read from the two verdict ledgers:

  test-plan review: 31 pass(es) over 6 unit(s), 25 rejected

  code review: 6 pass(es) over 6 unit(s), 6 rejected

  ratio: 0.19 code-review pass(es) per test-plan pass - the claim EP0207 is judged on, as a number
Unmeasured: BG0593, BG0594, BG0595, BG0596, BG0597, BG0598. They are excluded from the batch ratio - an unmeasured unit is not evidence that the estimate was right.
No unit in this batch is rated, so this sprint says nothing about the estimator's accuracy.

Forecast by `TOKENS_PER_POINT=25000`, recorded at plan time. OUT-OF-SAMPLE: forecast by the constants in force, on a sprint they were not fitted to. This is the only kind of row that tells you anything.

Ratio is estimate / actual: above 1 the plan over-forecast, below 1 it under-forecast. Nothing is re-fitted here - see VELOCITY.md for the trend across sprints, and change the constants only on evidence a human has looked at.
<!-- accuracy:end -->

- The forecast was wrong by an order of magnitude, and it was wrong about the CEREMONY rather than about the units. 2,020,985 tokens forecast at 44,427 per point; 11,034,109 spent on the main thread alone at 525,434 per point, with the subagent rounds uncounted on top of that. Every unit was correctly sized as 2 or 3 points and none was split, so the estimator did not misjudge the fixing. What it does not model at all is the number of independent review rounds a unit will draw, and eleven rounds over six units is where the money went. The next batch should be forecast on rounds as well as points - and CR0549 is a precondition for that, because the risk band that would predict rounds is currently computed from file size rather than change size.

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
| Delivery round 1 found BG0593's production change deletable with 916 tests green | fixed-in: BG0593, redesigned to a read root |
| Rounds 2-5 found five defects in the mutation and test-plan evidence | fixed-in: 20de1d1c..d9547254, one repair per round |
| Round 6 found changelog.d/BG0593.md describing the rejected symlink design | fixed-in: d9547254 |
| The dry-run class sweep truncates each probe to its first two elements | BG0601 |
| The close checklist derives its roster from an `_ck_` name prefix | BG0602 |
| `lint_stacked_verifiers` is applied at Draft and Ready but not at Open | BG0603 |
| `route.estimate` scores whole declared files, so the review tier is a constant | CR0549 |
| The test-plan gate is scoped by date alone and cannot be narrowed by risk | CR0550 |
| The delivery-round verdicts were not written to a ledger until the close | fixed-in: recorded at this close, and D0146 caps the rounds that produce them |
| BG0595 AC5's verifier is a static census rather than the comparison it states | declined: the row is declared unnameable and disclosed, the property being harness hermeticity, and the substantive claim is pinned by AC4 |

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

- Tokens: 11,034,109 (main thread only; the six review rounds ran as subagents and are NOT counted, so this is a lower bound) · Duration: 2,839 min elapsed against a 960 min appetite · Critic rejects: 11 (five plan-review rounds, six delivery rounds), of which four units were escalated for a non-converging repair

## Handoff

- [HO-0061](../handoffs/HO0061-every-instrument-this-run-touches-reports-only-a.md) - 0 remaining item(s): 0 copilot-tail, 0 judgement. Pick up with `sprint plan --worklist sdlc-studio/.local/handoff-worklist.txt`.
