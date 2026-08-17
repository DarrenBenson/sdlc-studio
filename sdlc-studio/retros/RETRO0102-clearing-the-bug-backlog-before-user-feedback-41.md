# RETRO-0102: Clearing the bug backlog before user feedback: 41 open bugs to 2, and what measurement overturned

> **Date:** 2026-08-15
> **Batch:** BG0535, BG0536, BG0542, BG0543, BG0557, US0667, US0668, US0669, BG0406, BG0457, BG0469, BG0488, BG0497, BG0522, BG0523, BG0528, BG0566, BG0569, US0670, BG0579, BG0580
> **Goal:** Every gate that prints a refusal performs one, and the acceptance criteria the README says are executable do run.
> **Delivered:** 19 / 19   **Blocked:** 0

## Delivered

All 19 batch units reached a terminal status. Beyond the batch, this run also cleared the open
bug backlog from **41 units / 117 points to 2 / 19** - 30 further bugs fixed, triaged or closed -
and cut v5.0.1 after finding that the verified-install path documented in the README had never
worked.

The three that mattered most were not in the batch at all:

* **BG0575** - the verified-install path had never worked, so v5.0.0 could not be installed as
  documented. v5.0.1 was cut for it.
* **BG0576** - `tag-check` read a locally recorded green and never asked the forge, so BOTH v5
  tags were cut over a CI that had been red for two days with every shipped guard reporting
  green. The failure class this repository exists to prevent, twice in two days.
* **BG0579** - the per-commit gate had outgrown the tool timeouts that run it, so a commit was
  KILLED rather than refused - and a kill reads as a hang, whose documented escape is
  `--no-verify`.

## Blocked / deferred

* **BG0490, BG0493** - triaged rather than built, on the operator's ruling. Each claim was
  re-measured: BG0490 is half lapsed (two of four instances no longer reproduce), BG0493 is
  fully live. Both carried with the measurement recorded.
* **BG0463** - excluded from scope by the operator.
* **BG0577** - delivered NARROWED. Its duplicate detector shipped; the repaired-but-open detector
  and the premise re-check did not, and the reasons are written on the artefact.
* **BG0579** - the boundary deferral shipped and cut the suite 934s to 569s, but the underlying
  arithmetic did not change: ~5,300 tests still run single-process on a 16-core machine.
  Parallelism needs `pytest-xdist`, a dependency change that is the operator's call.

## What went well

* **Independent review earned its cost.** Two adversarial passes REJECTED four of seven units
  with seven blocking findings. Two of those would have shipped real breakage: a swept verb that
  rewrites a tracked file (dirtying every fresh clone and CI), and a release guard that made
  every non-GitHub consumer permanently un-taggable.
* **Premise-checking before fixing.** Three bugs were overturned by measurement rather than
  repaired: BG0519's 4.5x gap measured 0.98x, BG0545's second half no longer reproduced, and
  BG0555's debt list held eight names already fixed. None would have been caught by reading.
* **The gates caught the author repeatedly** - the duplicate-verifier ratchet, the attribution
  census, `repo-writes`, the intra-record duplicate check. Each refused work of mine that looked
  finished.

## What was hard / what stalled

* **Mutants that do not reach the claim they name.** Six had to be re-chosen: one patched a
  message rather than the resolver, one a field map rather than the writer, one a label that
  satisfied the lane just as well as the real verifier, one never applied because its anchor was
  not unique. Each looked like evidence.
* **Two verdicts were registered without being executed**, and both were retracted on the record
  with the verb built earlier in this same run. The cause was entering a verdict from
  expectation rather than from the run.
* **Verification that ran where the author was standing.** A tracked-file write was invisible
  because gitignored state made the regeneration byte-identical; a control accepted the root path
  as evidence and so passed on a crash. Both were found by an independent pass in a clean
  worktree.
* **Self-matching shell patterns** cost two dead ends: a wait-loop whose `pgrep -f` matched its
  own command line waited for itself, and a `pkill -f` killed the shell that issued it.

## Lessons

* A mutant that cannot reach the code it names proves as little as a test that cannot fail. Six
  were re-chosen in this run: one patched a message instead of the resolver, one a field map
  instead of the writer, one a `manual` verifier that satisfied the lane exactly as the real one
  did. Each was registered, or nearly registered, as evidence.
* Verification run where the author is standing is not verification. A tracked-file write was
  invisible because gitignored state made the regeneration byte-identical; a control accepted the
  root path as evidence and so passed on a crash. Both were found only by a clean worktree.
* A guard a paraphrase can defeat is weak; one the OPPOSITE statement satisfies is inverted. Two
  spec-agreement guards were inverted, and either would have reported agreement while the
  specification stated the reverse of the code.
* A recorded list is a claim like any other and rots the same way. An eight-of-twelve stale debt
  list, a 12% fictional backlog, and a bug whose 4.5x premise measured 0.98x were all found by
  re-measuring rather than by reading.

## Carried lessons

* A mechanism that reaches no caller is inert, however well tested: `loop_guard budget` was fully
  wired to its data and had no caller at all.
* An absence is not an answer - a failed probe and a negative result are different facts, and
  collapsing them re-created BG0576's own defect inside its fix.
* A repair that is correct and UNGATED is not a repair.

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

| Issue | Ruling | Ruled by | Date |
| --- | --- | --- | --- |
| CR0534 | deferred | authoring session (recorded for the operator) | 2026-08-15 |
| CR0535 | deferred | authoring session (recorded for the operator) | 2026-08-15 |
| CR0536 | deferred | authoring session (recorded for the operator) | 2026-08-15 |
| CR0539 | deferred | authoring session (recorded for the operator) | 2026-08-15 |
| BG0463 | deferred | authoring session (recorded for the operator) | 2026-08-15 |
| BG0567 | not-stop-ship | authoring session (recorded for the operator) | 2026-08-15 |
| BG0578 | not-stop-ship | authoring session (recorded for the operator) | 2026-08-15 |
| BG0580 | not-stop-ship | authoring session (recorded for the operator) | 2026-08-15 |
| CR0509 | deferred | authoring session (recorded for the operator) | 2026-08-15 |
| CR0528 | deferred | authoring session (recorded for the operator) | 2026-08-15 |
| CR0529 | deferred | authoring session (recorded for the operator) | 2026-08-15 |
| CR0530 | deferred | authoring session (recorded for the operator) | 2026-08-15 |
| CR0531 | deferred | authoring session (recorded for the operator) | 2026-08-15 |
| CR0533 | deferred | authoring session (recorded for the operator) | 2026-08-15 |
| BG0490 | not-stop-ship | operator (triage ruling) | 2026-08-15 |
| BG0493 | not-stop-ship | operator (triage ruling) | 2026-08-15 |

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

* The batch was sized at 8 units / 960 minutes and delivered 19 batch units plus 30 further
  bugs over 5,271 wall-clock minutes. The ceiling was raised ON THE RECORD mid-run rather than
  overrun silently, and `over_appetite` stays true: raising a ceiling accepts an overrun, it
  does not erase it. The estimate missed because the run's purpose changed - three release-
  blocking findings appeared that were not in any plan.

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
| The verified-install path had never worked | fixed-in: v5.0.1 (BG0575) |
| Both v5 tags were cut over a red CI | fixed-in: BG0576 |
| The gate outgrew the timeouts that run it | fixed-in: BG0579 |
| Test attribution moves when a file mentions one more module | BG0578 |
| 26 planned mutants across 10 earlier units were never executed, 5 plans still scaffold | BG0580, all 35 executed and killed at this close |

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

* Tokens: harness-tracked, not recoverable from this session · Duration: 5,271 min wall-clock across three days · Critic rejects: 4 of 7 units reviewed, 7 blocking findings

## Handoff

* [HO-0058](../handoffs/HO0058-every-gate-that-prints-a-refusal-performs-one.md) - 0 remaining item(s): 0 copilot-tail, 0 judgement. Pick up with `sprint plan --worklist sdlc-studio/.local/handoff-worklist.txt`.
