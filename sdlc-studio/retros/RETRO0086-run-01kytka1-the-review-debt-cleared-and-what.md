# RETRO-0086: RUN-01KYTKA1: the review debt cleared, and what clearing it found

> **Date:** 2026-07-31
> **Batch:** BG0413, BG0438, BG0442, BG0443, BG0444, BG0447, BG0439, BG0415, BG0417, BG0418, BG0422, BG0423, BG0429, BG0440, BG0448, BG0449, BG0452, BG0430, BG0445, US0452, US0454, US0455, US0457, US0458, US0459, US0532, US0557, US0558, US0559, US0561, US0563, US0570, US0571, US0575, US0576, BG0454, US0453, US0456, US0460, US0465, US0560, US0562, US0569, US0572, US0574, US0555
> **Goal:** No gate reports green over something it did not check, and the standing review debt goes to zero HONESTLY: every unit at Review carries an independent recorded verdict, every rejection carries a filed finding with an executed reproduction, and every gate this batch touches either checks what it claims or states plainly that it did not.
> **Delivered:** 20 / 46   **Blocked:** 0

## Delivered

- 13 bugs to Fixed, 30 points - BG0417, BG0429, BG0430, BG0439, BG0440, BG0442, BG0443, BG0444, BG0445, BG0447, BG0449, BG0452, BG0454
- 7 stories to Done, 27 points - US0453, US0455, US0456, US0460, US0557, US0559, US0563: the units that passed independent adversarial review with no blocking finding, each carrying a recorded verdict, recorded evidence, and the reviewer of record's signature
- 26 units of standing review debt carry an independent recorded verdict and its evidence, which is the goal's first clause and the thing this batch existed to do
- 5 repairs found BY the review and closed inside it - BG0456, BG0459 (part), BG0464, BG0465, and BG0440's falsified criterion
- Clause three closed on its second limb: six guards the sprint did not repair now STATE their real limit in their own prose, each with the measured evidence, and the shipped doctrine no longer tells a consuming project that the checklist and the cycle cannot part

## Blocked / deferred

- Nothing was blocked. 19 stories remain at Review carrying a recorded REJECT, and 7 bugs remain Open - all carried forward on the operator's ruling that bugs may carry, with findings filed and reproductions executed.

## What went well

- The review found what the sprint was aimed at. Seven seats over three charters applied roughly 180 mutants and returned 19 REJECTs, every one of them a gate reporting green over something it never checked - which is the sprint goal restated as a measurement rather than an intention.
- Pointing a reviewer at the machinery that enforces review paid for the whole exercise. BG0464 - an author retiring the REJECT that blocks their own work with one hand-appended line - was found by the seat reviewing exactly that, and it was the only finding rated Critical.
- The repo's own guards corrected the author repeatedly and cheaply: the verify ratchet refused a duplicate selector that would have left two criteria discriminating nothing, and `verify_ac run --from-run` caught a criterion whose verifier selected an empty set. Both were faster than a reviewer and neither needed one.
- Every repair was mutation-verified rather than asserted. Three separate times the first attempt at a regression test passed with AND without the guard it was written for, and each was caught before the commit rather than by the next reviewer.

## What was hard / what stalled

- Seven reviewers for seven opened at a stale base and each had to diagnose it before starting. They noticed only because `critic.py brief` refused an unknown id; a reviewer who missed it would have returned a real-looking verdict about the wrong tree. Filed as CR0509.
- One seat reported the shipped suite RED on main at six failures. Re-measured on main it is green under both the declared `unittest discover` command (5586 OK) and pytest (5585 passed). Its worktree was 188 commits behind. The claim was recorded as CORRECTED on the verdict rather than accepted or quietly dropped - and the seat had already caught the same artefact itself, re-running four mutants it had wrongly scored KILLED against a baseline it believed red.
- The gate budget is now 500-517s against a 380s ceiling, +58% to +63% over baseline, and it degraded across this sprint rather than holding. BG0415 is open on it and getting worse.
- 74 points of stories cannot reach Done on the strength of this session's work, because their remaining work is a repair the review demanded. That is the correct outcome and it was not the planned one.

## Lessons

- A ratio or threshold test cannot report its own inertness, so the property that makes it meaningful needs its own assertion. US0532's corpus pin held at 2.0 with the cache live and 2.0 with it neutered - a ninefold read regression moved the asserted number by nothing - because the fixture issued a CONSTANT six lookups whatever the corpus size, making both branches linear. The scaling is a different fact from the ratio and now has its own test.
- A guard that reads a document and compares it against a projection of itself can never fail in the reverse direction. `named = _backticked(block) & types` then asserting `types - named == set()` makes `named` a subset by construction, so three mutants - removing a shipped lane, removing a drift kind, and inventing a fictional lane in the prose - all survived a guard whose criteria claim it "fails in either direction".
- A whole-file substring assertion over a document that also carries a Revision History is satisfied by the Revision History row describing the change being asserted. Both passages stating the token premise could be gutted and the guard stayed green.
- The grade of authority a correction needs should scale with the direction its mistake fails. Retiring an APPROVE weakly loses an approval and the gate refuses; retiring a REJECT weakly deletes the only record that blocks the unit. One flag tested for plain truthiness served both, and the backstop written for exactly that hand-append was consulted by only one of the two gates it should have guarded.
- A floor tolerates the failure it was written to catch. `assertGreaterEqual(len(left), 6)` over the retro template's worked examples could not see a marker going missing, which is why three demonstration rows carried none and a wholly unreplaced scaffold validated as three dispositioned findings.

## Carried lessons

The 5 that matter most for the NEXT batch, chosen now rather than ranked from the whole
store. A ranking is a fact about the past; this is a decision, re-made every retro. Bullets,
not a numbered list, and drop one for each you add (`lessons carry --displaces`).

- A test that passes with AND without the guard it was written for is not a test. Apply the mutant before believing the assertion - three of this sprint's own repairs failed this on the first attempt.
- A guard comparing a document against a projection of itself has one direction, whatever its criteria claim. Mutate the document AND the code.
- An absence is not an answer: a scan that saw nothing and a scan that could not see must not render the same. `_ck_known_issues` reported "none carried" for a blind scan while its sibling row reported the identical blindness as unreadable, on the same page.
- Verify the premise before building on it, and re-measure a claim before repeating it. One seat's "the suite is red" was true of its tree and false of main; the author's own "25 Done stories" was false and had already reached shipped code.
- A stale base is invisible unless something refuses. Seven reviewers hit it and were saved by an id lookup, not by design.

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
| BG0457 | not-stop-ship | operator (bugs may carry forward) | 2026-07-31 |
| BG0458 | not-stop-ship | operator (bugs may carry forward) | 2026-07-31 |
| BG0459 | not-stop-ship | operator (bugs may carry forward) | 2026-07-31 |
| BG0460 | not-stop-ship | operator (bugs may carry forward) | 2026-07-31 |
| BG0461 | not-stop-ship | operator (bugs may carry forward) | 2026-07-31 |
| BG0462 | not-stop-ship | operator (bugs may carry forward) | 2026-07-31 |
| BG0463 | not-stop-ship | operator (bugs may carry forward) | 2026-07-31 |
| BG0413 | not-stop-ship | operator (bugs may carry forward) | 2026-07-31 |
| BG0415 | accepted-risk | operator - the gate budget is over and degrading, +58% since baseline | 2026-07-31 |
| BG0418 | not-stop-ship | operator (bugs may carry forward) | 2026-07-31 |
| BG0422 | not-stop-ship | operator (bugs may carry forward) | 2026-07-31 |
| BG0423 | not-stop-ship | operator (bugs may carry forward) | 2026-07-31 |
| BG0438 | not-stop-ship | operator (bugs may carry forward) | 2026-07-31 |
| BG0448 | not-stop-ship | operator (bugs may carry forward) | 2026-07-31 |
| CR0509 | not-stop-ship | operator (bugs may carry forward) | 2026-07-31 |
| BG0466 | not-stop-ship | operator (bugs may carry forward) - raised by the rejoinder review after this table was first written, which is the checklist doing its job | 2026-07-31 |

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
| BG0413 | 2 | 92,286 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| BG0438 | 2 | 92,286 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| BG0442 | 2 | 92,286 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| BG0443 | 2 | 92,286 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| BG0444 | 2 | 92,286 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| BG0447 | 2 | 92,286 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| BG0439 | 1 | 46,143 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| BG0415 | 3 | 138,429 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| BG0417 | 3 | 138,429 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| BG0418 | 3 | 138,429 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| BG0422 | 3 | 138,429 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| BG0423 | 3 | 138,429 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| BG0429 | 3 | 138,429 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| BG0440 | 3 | 138,429 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| BG0448 | 3 | 138,429 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| BG0449 | 3 | 138,429 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| BG0452 | 3 | 138,429 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| BG0430 | 2 | 92,286 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| BG0445 | 2 | 92,286 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| US0452 | 3 | 138,429 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| US0454 | 3 | 138,429 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| US0455 | 3 | 138,429 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| US0457 | 3 | 138,429 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| US0458 | 3 | 138,429 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| US0459 | 3 | 138,429 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| US0532 | 3 | 138,429 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| US0557 | 3 | 138,429 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| US0558 | 3 | 138,429 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| US0559 | 3 | 138,429 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| US0561 | 3 | 138,429 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| US0563 | 3 | 138,429 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| US0570 | - | - | - | **UNFORECAST** (no plan-time forecast recorded; no telemetry token record) | - | - | - | - |
| US0571 | - | - | - | **UNFORECAST** (no plan-time forecast recorded; no telemetry token record) | - | - | - | - |
| US0575 | - | - | - | **UNFORECAST** (no plan-time forecast recorded; no telemetry token record) | - | - | - | - |
| US0576 | - | - | - | **UNFORECAST** (no plan-time forecast recorded; no telemetry token record) | - | - | - | - |
| BG0454 | 2 | 92,286 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| US0453 | 5 | 230,715 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| US0456 | 5 | 230,715 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| US0460 | 5 | 230,715 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| US0465 | 5 | 230,715 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| US0560 | 5 | 230,715 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| US0562 | 5 | 230,715 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| US0569 | - | - | - | **UNFORECAST** (no plan-time forecast recorded; no telemetry token record) | - | - | - | - |
| US0572 | - | - | - | **UNFORECAST** (no plan-time forecast recorded; no telemetry token record) | - | - | - | - |
| US0574 | - | - | - | **UNFORECAST** (no plan-time forecast recorded; no telemetry token record) | - | - | - | - |
| US0555 | 8 | 369,144 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| **Batch (rated units only)** | **0** | **0** | **0** | - | **-** | | **-** | - |

**0 of 46 unit(s) measured; 39 of 46 forecast at plan time.**

**Velocity (points/elapsed-hour): UNMEASURED.** No run-state elapsed for this sprint (an interactive sprint's wall-clock would count operator-away gaps as sprint time). Supply a real elapsed with `accuracy --elapsed-hours H` to record it - descriptive, never a target.

  secondary (points/worker-hour): UNMEASURED - no runner worker-time records (an interactive sprint has none).
Unmeasured: BG0413, BG0438, BG0442, BG0443, BG0444, BG0447, BG0439, BG0415, BG0417, BG0418, BG0422, BG0423, BG0429, BG0440, BG0448, BG0449, BG0452, BG0430, BG0445, US0452, US0454, US0455, US0457, US0458, US0459, US0532, US0557, US0558, US0559, US0561, US0563, BG0454, US0453, US0456, US0460, US0465, US0560, US0562, US0555. They are excluded from the batch ratio - an unmeasured unit is not evidence that the estimate was right.
Unforecast: US0570, US0571, US0575, US0576, US0569, US0572, US0574. No plan-time forecast was recorded for them, so they are excluded too. The estimate is NOT re-derived from today's constants: a number computed at judgement time, by the model being judged, is not a prediction.
No unit in this batch is rated, so this sprint says nothing about the estimator's accuracy.

Forecast by `TOKENS_PER_POINT=25000`, recorded at plan time. OUT-OF-SAMPLE: forecast by the constants in force, on a sprint they were not fitted to. This is the only kind of row that tells you anything.

Ratio is estimate / actual: above 1 the plan over-forecast, below 1 it under-forecast. Nothing is re-fitted here - see VELOCITY.md for the trend across sprints, and change the constants only on evidence a human has looked at.
<!-- accuracy:end -->

- The points estimate priced DELIVERY and this batch spent most of its cost on REVIEW, so the per-unit ratio will read badly for the 19 rejected units and that reading is correct rather than a miss. 101 points of review debt were planned as if the remaining work were a signature; the review established that the remaining work was repair. The lesson for the next forecast is that a unit standing at Review is not nearly-done - it is unmeasured, and its cost is unknown until somebody looks.

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
| An author can retire the REJECT blocking their own work with one hand-appended supersession line | fixed-in: ad989eea |
| A ruling verb bypasses the destination check, so a tick citing an artefact nothing holds is accepted | fixed-in: 6872c5a5 |
| The corpus-read pin is inert - its fixture never scales, so the ratio is invariant to the cache | fixed-in: 6872c5a5 |
| Three retro demonstration rows carry no marker, so an unreplaced scaffold validates as filled-in | fixed-in: d3b588af |
| An acceptance criterion its own later fix had falsified, with a verifier selecting nothing | fixed-in: e25f307d |
| Four spec-agreement guards pin prose to prose and cannot fail in the reverse direction | BG0457 |
| Five checklist rows report a state they never established, one of them failing open | BG0458 |
| The close discards the retro validator's report on a zero exit | BG0459 |
| The dry-run reports a chain step as neither refusing nor unevaluated | BG0460 |
| The checklist's drift guard certifies two rows unchecked, and a waiver records no authoriser | BG0461 |
| The version guard's discovery test cannot tell discovery from the hardcoded fallback | BG0462 |
| Twenty non-blocking findings - stale counts, dead code, unmarked truncation, over-claiming prose | BG0463 |
| A review worktree opens at a stale base, seven reviewers for seven | CR0509 |
| `-` passes the trust-boundary test in three places, being a non-empty string and this repo's own placeholder for absent | declined: recorded on BG0464 rather than widened into that repair mid-sprint; it needs its own unit, and no gate depends on it alone |

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

- Tokens: not-yet-captured · Duration: one interactive session · Critic rejects: 19 of 26 units reviewed

## Handoff

- [HO-0038](../handoffs/HO0038-no-gate-reports-green-over-something-it-did.md) - 0 remaining item(s): 0 copilot-tail, 0 judgement. Pick up with `sprint plan --worklist sdlc-studio/.local/handoff-worklist.txt`.
