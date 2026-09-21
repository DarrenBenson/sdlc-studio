# RETRO-0119: the backlog tells the truth: what 38 requests and 24 claims said when somebody finally asked them

> **Date:** 2026-09-21
> **Batch:** BG0718, US0848, US0849, US0850, US0851, US0852, US0853, US0854
> **Goal:** the backlog tells the truth: every stalled request and stale finding carries a dated ruling, and the state that let them accumulate cannot rebuild
> **Delivered:** 7 / 8   **Blocked:** 1

## Delivered

- US0848 - the `unruled` lens: a discovery request that is In Progress, finished by its children and never judged is reported, advisory, naming what clears it. Three mutants applied and killed.
- US0849 - the close-and-ceremony cluster ruled: 9 requests, 5 returned to Proposed, 1 retired as overtaken, 3 confirmed correctly in progress.
- US0850 - the review-and-critic cluster ruled: 8 requests, 3 returned to Proposed, 1 retired (it had retracted itself), 4 correctly in progress.
- US0851 - the evidence and gate-cost cluster ruled: 10 requests, and the run's best outcome - CR0547 and CR0548 found ALREADY DELIVERED and closed.
- US0852 - the config, docs and stakeholder cluster ruled: 11 requests, 10 returned to Proposed, RFC0058 confirmed in progress on the distinction that an RFC's deliverable is a ruling.
- US0853 - BG0463 re-triaged: 24 claims found where twenty were expected, each ruled individually, 15 survivors filed as BG0723-BG0730 and CR0592.
- US0854 - the four 8-pointers resolved (two decomposed into US0855-US0859, two retired with their retracted parent) and the US0793/US0794 pair ruled genuinely distinct.

## Blocked / deferred

- BG0718 - REJECTED a third time at plan review and escalated to the operator for the second time. Six criteria, six mutants killed, three independent rejections, every one a real defect. Its code is in force; the bug stays open by the operator's standing ruling that it is not closed on its author's say-so.

## What went well

- **The audit paid for itself on its third cluster.** CR0547 and CR0548 had been finished since August and were held open by a shared epic's Draft status - the request was done, the link was not. Nothing but reading them against HEAD would have found that.
- **Parallel agents on file-disjoint clusters worked.** Four agents produced checkable evidence - file:line, commit sha, command output - and the rulings stayed with the session as D0222 required. Judging a cluster together mattered: three of the close-cluster requests turned out to be one pressure at three moments, and CR0550 was found to have retracted itself in its own revision history.
- **Three gates caught defects in this run's own work and none was repaired to make the run pass.** A shell-hazard guard found the residue of a mangled edit; the verify-ratchet found four cluster stories sharing one verifier; the derived-only ceiling went red on the run's own filings.

## What was hard / what stalled

- **The guard this run built does not guard the state this run cleared.** US0848 reports zero against the real backlog, because all 37 stalled requests have an unresolved child. It catches a request nobody closed; what accumulated was a request everybody abandoned. Filed as BG0722 rather than claimed as met - the run's goal says the state cannot rebuild, and it still can.
- **Four of my own verifiers were narrower than the criteria they served**, each caught by execution rather than by review: two used `f['kind']` where the tool emits `lens`, one demanded a duplicate disappear when the criterion also allowed ruling it distinct, and one counted 5 lines where 24 rulings were required.
- **Decomposing a unit duplicates its verifiers.** Carrying criteria verbatim into the parts - which is what keeps the scope provably unchanged - leaves the superseded parent holding live selectors its successors now own. Six gate failures across four commit attempts came from this one cause.

## Lessons

- A backlog count is a claim about state, and `In Progress` is the weakest link in it: in one cluster of eleven, not a single commit naming any request was a `feat` or a `fix`. Read the commits, not the status.
- A guard built to stop a state rebuilding must be run against the state that actually accumulated, the same day, before the run claims its goal.

## Carried lessons

The 5 that matter most for the NEXT batch, chosen now rather than ranked from the whole
store. A ranking is a fact about the past; this is a decision, re-made every retro. Bullets,
not a numbered list, and drop one for each you add (`lessons carry --displaces`).

- EXAMPLE - replace this. A mechanism that reaches no caller is inert, however well it is tested. <!-- example -->
- EXAMPLE - replace this. An absence is not an answer: an empty result and an unanswerable question are different facts. <!-- example -->
- EXAMPLE - replace this. A repair breaks its neighbours, and a rename is cross-unit coupling. <!-- example -->
- EXAMPLE - replace this. An enumerated list silently exempts what it forgot. <!-- example -->
- EXAMPLE - replace this. Verify the premise before building on it. <!-- example -->

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
| BG0718 | not-stop-ship | operator, D0226 and the standing ruling on its escalation | 2026-09-21 |
| BG0722 | not-stop-ship | the run that raised it - the gap is recorded, not claimed as met | 2026-09-21 |
| US0853 | not-stop-ship | the run itself, recorded rather than waived - see the criterion and BG0731 | 2026-09-21 |
| BG0732 | not-stop-ship | the wall was recorded, not moved; the census cleared by authoring criteria | 2026-09-21 |

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
(`accuracy --tokens-from-harness`, run by `sprint close` as it PREPARES the run) and the velocity row
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
| BG0718 | 2 | 101,036 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| US0848 | 3 | 151,554 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| US0849 | 5 | 252,590 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| US0850 | 5 | 252,590 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| US0851 | 5 | 252,590 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| US0852 | 5 | 252,590 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| US0853 | 5 | 252,590 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| US0854 | 3 | 151,554 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| **Batch (rated units only)** | **0** | **0** | **0** | - | **-** | | **-** | - |

**0 of 8 unit(s) measured; 8 of 8 forecast at plan time.**

**Sprint tokens/point: 2,200,303** (4,400,606 tokens over 2 delivered points, harness-tracked). The token count is deterministic (supply it with `accuracy --tokens N`) - not UNMEASURED. A descriptive velocity, never a target.

**Velocity (points/elapsed-hour): UNMEASURED.** No run-state elapsed for this sprint (an interactive sprint's wall-clock would count operator-away gaps as sprint time). Supply a real elapsed with `accuracy --elapsed-hours H` to record it - descriptive, never a target.

  secondary (points/worker-hour): UNMEASURED - no runner worker-time records (an interactive sprint has none).

Review passes, by phase - read from the two verdict ledgers:

  test-plan review: 14 pass(es) over 8 unit(s), 7 rejected

  code review: NOT IN FORCE for this run - no verdict of that phase covers any of its units, which is not the same as a run that held them and spent nothing
Unmeasured: BG0718, US0848, US0849, US0850, US0851, US0852, US0853, US0854. They are excluded from the batch ratio - an unmeasured unit is not evidence that the estimate was right.
No unit in this batch is rated, so this sprint says nothing about the estimator's accuracy.

Forecast by `TOKENS_PER_POINT=25000`, recorded at plan time. OUT-OF-SAMPLE: forecast by the constants in force, on a sprint they were not fitted to. This is the only kind of row that tells you anything.

Ratio is estimate / actual: above 1 the plan over-forecast, below 1 it under-forecast. Nothing is re-fitted here - see VELOCITY.md for the trend across sprints, and change the constants only on evidence a human has looked at.
<!-- accuracy:end -->

- The estimate is not readable as calibration this run, and the reason is recorded rather than
  hidden: BG0718 carries 2 of the 33 points for work delivered BEFORE the run opened (D0226), so
  velocity reads 2 high and tokens-per-point reads low by that amount. The seven ruling stories
  were also sized as delivery when most of their cost is reading and judging - a sweep's points
  measure artefacts handled, not code written, and comparing them against a build run's ratio
  would be comparing two different things. What IS readable: the four cluster stories were sized
  5, 5, 5, 5 for 9, 8, 10 and 11 requests, and the effort tracked the count closely enough that
  per-artefact sizing looks sound for the next sweep.

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
| The guard reports zero against the state the sweep cleared | BG0722 |
| The duplicate lens cannot tell a scope-split, or a control, from a duplicate | BG0721 |
| Filing a Low finding recreates the bucket D0217 retired the day before | BG0731 |
| The derived-only ceiling is absolute, so filing findings breaches it | BG0732 |
| 15 survivors of BG0463, filed as their own artefacts with criteria | BG0723, BG0724, BG0725, BG0726, BG0727, BG0728, BG0729, BG0730, CR0592 |
| A stop-ship ruling outlives its finding and blocks every close | BG0730 |

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

- Tokens, duration and reject counts are derived by `sprint close` into the report of record;
  this line is left to that derivation rather than hand-copied, which is the defect RETRO0118's
  run filed as BG0720 (a figure scraped from retro prose rather than taken from the record).
- Critic rejects this run: 1 unit rejected, 3 times, all on BG0718's test plan - and every one
  found a real defect the previous round had missed.

## Handoff

- [HO-0079](../handoffs/HO0079-the-backlog-tells-the-truth-every-stalled-request.md) - 7 remaining item(s): 0 copilot-tail, 7 judgement. Pick up with `sprint plan --worklist sdlc-studio/.local/handoff-worklist.txt`.
