# RETRO-0093: RUN-01KZ5YXM: the charter queue - more, smaller runs becomes a command

> **Date:** 2026-08-04
> **Batch:** US0487, US0488, US0489, US0490, US0491, US0492
> **Goal:** More, smaller runs is a command rather than an intention: a sprint charter is a first-class artefact carrying its own goal, scope rule, appetite and seat review, the next run is materialised from the head charter against the backlog as it stands at that moment, and calling a sprint at a point returns its unstarted remainder to the queue instead of losing it.
> **Delivered:** 6 / 6   **Blocked:** 0

## Delivered

- US0487 - a sprint charter is a first-class artefact (`SC`, `sdlc-studio/charters/`), its prefix, create status and terminal set DERIVED from the shared registry rather than restated
- US0488 - `sprint next` resolves the head charter against the backlog as it stands at that moment, refusing on an open run, an unresolvable scope or an empty one, each leaving the queue untouched
- US0489 - the queue is inspectable and editable: show, reorder, cancel, clear. Cancel withdraws rather than deletes and keeps its reason
- US0490 - a charter carries its own goal review under `## Seat review`, so it travels between working copies; the runner is recorded beside the reviewer and a match is stated, never enforced
- US0491 - `sprint call` descopes the unstarted remainder to the BACKLOG and runs the close, so a called sprint is finished rather than abandoned
- US0492 - the queue lifecycle is documented beside the run lifecycle, with the docs pinned to the parser in both directions

## Blocked / deferred

- none - every unit reached Review and was approved at round 3

## What went well

- The refusal curve fell 8 -> 4 -> 2 -> 0 -> 0 -> 0 across the six units. The brownfield tax turned out to be paid once per SURFACE rather than once per unit: adding a CLI verb to this system obliges five things beyond the code - an invocation in the help page, a verifier that enters `main()`, a ceremony-or-not declaration, an accurate `Affects`, and a nested `--root` defaulting to SUPPRESS - and once known they were applied up front.
- Every design decision that could be reversed later by somebody who does not know why is written where they will find it: absence is not rank zero; cancel withdraws rather than deletes; only the head is resolved; the remainder goes backward to the backlog, never forward to the next charter.
- The mutation pass earned its place on US0492, where two mutants SURVIVED the first draft - and the reason was the criterion itself. AC1 said the expected set must be read from the parser rather than a list in the check, and the first version kept a hardcoded tuple: the exact defect the criterion forbids, written into the test meant to enforce it.

## What was hard / what stalled

- US0491 took THREE review rounds and the tooling escalated it to the operator for non-convergence. Round 1: `call` printed `now close it against the goal` and returned 0 without closing. Round 2: the repair could not execute at all - `cmd_close` reads `args.goal_verdict` unguarded and `call` defined no such flag, so every invocation died on an uncaught AttributeError.
- Both failures were the SAME error: satisfying a gate rather than the criterion. Round 1 repointed AC1's verifier onto a CLI test to clear the lane-check, and the new test asserted only `rc==0` and printed strings. Round 2's verifier stubbed `cmd_close` with a lambda, proving the close was CALLED while being structurally unable to see it exploded.
- Both shipped GREEN through the full suite, `verify_ac`, the lane-check and `gate.py`. Round 2's version passed every automated check in the repository while being a verb that could not run.

## Lessons

- Satisfying a gate is not the same as satisfying the criterion, and when the two pull apart the criterion wins. Two rejections in this run were caused by moving a verifier to clear a lane-check, each time onto ground where the criterion's own gap was invisible.
- A stub is not the shipped entry point. A verifier that monkeypatches the collaborator under test proves the call happened and cannot see that it failed - which is how a verb that tracebacked on every invocation passed the suite, verify_ac, the lane-check and the gate.
- A mutant that removes ONE of two sufficient fixes measures less than it appears to. The honest mutant reproduces the exact state that shipped; a partial one survives and reads as coverage.
- A file-disjoint unit is not necessarily an independent one. Three couplings in this epic were invisible to a seam check: criteria that read what another unit creates, a guard requiring each verb to document itself, and a shared registry every verb must declare into.

## Carried lessons

The 5 that matter most for the NEXT batch.

- Satisfying a gate is not the same as satisfying the criterion; when they pull apart, the criterion wins.
- A stub is not the shipped entry point - type the command before asking for review.
- A mutant that removes one of two sufficient fixes measures less than it appears to.
- A test that opens the mechanism itself proves the mechanism and never its caller.
- Verify the premise before building on it.

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
| BG0457 | not-stop-ship | Darren Benson (operator, reviewer of record) | 2026-08-04 |
| BG0463 | not-stop-ship | Darren Benson (operator, reviewer of record) | 2026-08-04 |
| BG0469 | not-stop-ship | Darren Benson (operator, reviewer of record) | 2026-08-04 |
| BG0486 | not-stop-ship | Darren Benson (operator, reviewer of record) | 2026-08-04 |
| BG0500 | not-stop-ship | Darren Benson (operator, reviewer of record) | 2026-08-04 |
| BG0507 | not-stop-ship | Darren Benson (operator, reviewer of record) | 2026-08-04 |
| BG0508 | not-stop-ship | Darren Benson (operator, reviewer of record) | 2026-08-04 |
| BG0509 | not-stop-ship | Darren Benson (operator, reviewer of record) | 2026-08-04 |
| BG0510 | not-stop-ship | Darren Benson (operator, reviewer of record) | 2026-08-04 |
| BG0512 | not-stop-ship | Darren Benson (operator, reviewer of record) | 2026-08-04 |
| CR0509 | not-stop-ship | Darren Benson (operator, reviewer of record) | 2026-08-04 |
| CR0510 | not-stop-ship | Darren Benson (operator, reviewer of record) | 2026-08-04 |
| CR0528 - the installed copy is only reconciled at a close | not-stop-ship | Darren Benson (operator, reviewer of record) | 2026-08-04 |
| CR0529 - the prior-art check is scoped to the reviewer, not the author | not-stop-ship | Darren Benson (operator, reviewer of record) | 2026-08-04 |
| CR0530 - the planner reports clusters, not the parallelisable fraction | not-stop-ship | Darren Benson (operator, reviewer of record) | 2026-08-04 |
| BG0516 - the close reports a gate refusal it could not attribute, where the gate named its lane | not-stop-ship | Darren Benson (operator, reviewer of record) | 2026-08-04 |
| BG0517 - the close-loop cap stops a loop that has already converged | not-stop-ship | Darren Benson (operator, reviewer of record) | 2026-08-04 |
| BG0514 - queue show is blind during a run, reusing the materialiser's open-run refusal | not-stop-ship | Darren Benson (operator, reviewer of record) | 2026-08-04 |
| BG0515 - the queue has no exit: nothing sets Spent, so a charter re-materialises forever | not-stop-ship | Darren Benson (operator, reviewer of record) | 2026-08-04 |
| CR0531 - a scope query cannot express a decomposition, so SC0001's two scope fields disagree | not-stop-ship | Darren Benson (operator, reviewer of record) | 2026-08-04 |
| BG0513 - run-suite.sh is intermittently red and the failing test cannot be named | not-stop-ship | Darren Benson (operator, reviewer of record) | 2026-08-04 |

> **ESCALATED, and recorded here rather than only in the ledger.** The tooling notified the
> operator that US0491 was rejected twice and was not converging. That is the operator's own
> rule mechanised, and it fired correctly. The run continued to its close because the
> escalation notifies rather than blocks and D0126 grants standing sign-off - but the ruling
> remains the operator's to reverse, and the third-round approval should be read knowing two
> earlier attempts passed every automated check in this repository while being wrong.

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
| US0487 | 5 | 230,715 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| US0488 | 5 | 230,715 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| US0489 | 5 | 230,715 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| US0490 | 3 | 138,429 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| US0491 | 5 | 230,715 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| US0492 | 3 | 138,429 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| **Batch (rated units only)** | **0** | **0** | **0** | - | **-** | | **-** | - |

**0 of 6 unit(s) measured; 6 of 6 forecast at plan time.**
Unmeasured: US0487, US0488, US0489, US0490, US0491, US0492. They are excluded from the batch ratio - an unmeasured unit is not evidence that the estimate was right.
No unit in this batch is rated, so this sprint says nothing about the estimator's accuracy.

Forecast by `TOKENS_PER_POINT=25000`, recorded at plan time. OUT-OF-SAMPLE: forecast by the constants in force, on a sprint they were not fitted to. This is the only kind of row that tells you anything.

Ratio is estimate / actual: above 1 the plan over-forecast, below 1 it under-forecast. Nothing is re-fitted here - see VELOCITY.md for the trend across sprints, and change the constants only on evidence a human has looked at.
<!-- accuracy:end -->

- 26 points across 6 units. The points were accurate for the CODE and blind to the REVIEW: US0491 is a 5-point unit that consumed three review rounds and two repairs, while US0490 and US0492 landed clean first time. What the estimate misses is not size but how far a unit sits from a surface the author already understands.

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
| US0491 AC1 was unmet: `call` advised a close rather than running one | fixed-in: c1b843b9 |
| AC1's verifier had been repointed onto a test that could not see the gap | fixed-in: 59d96805 |
| The round 1 repair could not execute - uncaught AttributeError on every path | fixed-in: 59d96805 |
| The round 2 verifier stubbed the collaborator under test | fixed-in: 59d96805 |
| changelog.d and help/sprint.md falsely claimed the close paperwork runs | fixed-in: 59d96805 |
| `next`'s docstring claimed it opened a run; `--dry-run` contrasted two identical paths | fixed-in: c1b843b9 |
| Three units over-declared or under-declared their Affects | fixed-in: 9944e276 |
| `queue show` is blind during a run | BG0514 |
| The queue has no exit - nothing sets `Spent` | BG0515 |
| A scope query cannot express a decomposition | CR0531 |
| `--note` without `--goal-verdict` is silently dropped | declined: pre-existing in `close` and inherited verbatim, not introduced here - it belongs with the close-cost work SC0001 carries |
| The close could not attribute a gate refusal, burning four rounds | BG0516 |
| The loop cap stopped a converged close | BG0517 |
| The bounded `--file-and-close` exit is unreachable in one act from `call` | declined: `sprint close --file-and-close` after the descope is correct and documented; adding a second route would duplicate the close's own flag surface |

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

- Tokens: {{tokens}} · Duration: {{duration}} · Critic rejects: {{rejects}}
