# RETRO-0074: CR0421 delivered - a sprint close can converge (batch mutable, correctness batch-scoped, currency by record)

> **Date:** 2026-07-26
> **Batch:** US0433, US0434, US0435, US0436 (EP0162)
> **Goal:** Deliver CR0421 - a sprint close can converge: batch mutable (drop/add), correctness batch-scoped, a growing set offers the bounded exit, currency judged by the review record
> **Delivered:** 4 / 4   **Blocked:** 0

## Delivered

- US0433 - `sprint batch drop <id> --reason` / `batch add <id>` mutate an open run's approved batch, recorded in `batch_changes`; drop releases the done-gate, distinct from Deferred (which leaves the unit gated). Replaces the hand-edited `run-state.json` the CR's addendum described.
- US0434 - the sprint close's conformance lane is scoped to its batch (explicit `scope_ids` threaded `detect_conformance` -> `gate._conformance` -> `run_gate(conformance_scope=...)` -> the close preflight). Out-of-batch debt no longer blocks an in-batch close; repo-global stages stay at full strength; a `--release` tag still judges everything. Removes the grandfather-bump pressure.
- US0435 - a growing outstanding set names the way out honestly: `--file-and-close` for the deferrable (ceremony) items, and "clear the lanes" for hard correctness blockers it would refuse. Made only when growing.
- US0436 - review-currency judged by the review RECORD (`.local/review-state.json`), not the anchor's commit time: an artefact is stale only when the anchor commit-time AND the record both say so. Fixes the byte-identical re-stamp trap; the invariant is stated in `reference-sprint.md`.

## Blocked / deferred

- None. All four reached Review with executable ACs passing; Done follows the reviewer-of-record sign-off (two-role gate, units past `review.two_role_after` 192).

## What went well

- Direct field evidence for every AC: this session's own v5 close (RUN-01KYAHY9) reproduced every symptom CR0421 diagnoses, so the ACs were anchored in a real failure, not a hypothetical.
- The independent adversarial review (fresh context, RFC0051/D0059) APPROVEd with no MAJOR and found a real UX defect (MINOR-2) the author's own tests passed over - the two-role gate earning its keep.
- Each unit shipped TDD-first with a mutation check per guard (drop filter, reason guard, add-append, the conformance narrow precedence, the run_gate binding, the review-currency hybrid, the deferrable-stage filter) - every mutant killed.

## What was hard / what stalled

- US0436 was the riskiest: `_review_current` is a load-bearing gate lane with 13 existing tests built on the LATEST.md commit-time model and no review-state.json in their fixtures. A wholesale switch to record-based judgment would have broken them and risked weakening the gate. The hybrid ("stale only if anchor AND record agree") was the safe path - the record can only make an artefact MORE current, never falsely pass a changed one - and it preserved all 13.
- Same-second git commit granularity: the US0436 fixture had to backdate the anchor commit deterministically (`GIT_COMMITTER_DATE`), or `stale_by_anchor` collided and the test proved nothing.
- A parallel session's untracked `BG0300` tripped the shell-hazard fingerprint (a false positive on aligned code-excerpt spacing), blocking the commit gate; resolved by rewording its whitespace with operator approval, per the shared-repo discipline.

## Lessons

- A batch-scoping or record-based "make-it-pass-here" gate change must be proven it cannot make a genuinely-broken close pass. The safe shape is a narrowing that only ever makes things MORE current / smaller-scoped while the repo-global and in-batch strength is held constant - and a test that asserts the exact count delta, so a scope that silently dropped a global failure would fail. <!-- record it: lessons add (project tier). Promote with --global only what generalises beyond this repo -->
- An "offer the exit" affordance must be honest about what the exit actually does: `--file-and-close` refuses hard correctness lanes, so offering it for a set of `gate` blockers dangles a dead-end. The independent review caught this where the author's tests (which used synthetic non-deferrable stages) asserted only that the string appeared.

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
| US0433 | 3 | 157,725 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| US0434 | 3 | 157,725 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| US0435 | 2 | 105,150 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| US0436 | 3 | 157,725 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| **Batch (rated units only)** | **0** | **0** | **0** | - | **-** | | **-** | - |

**0 of 4 unit(s) measured; 4 of 4 forecast at plan time.**

**Sprint tokens/point: 149,195** (1,641,143 tokens over 11 delivered points, harness-tracked). The token count is deterministic (supply it with `accuracy --tokens N`) - not UNMEASURED. A descriptive velocity, never a target.

**Velocity: 3.09 points/elapsed-hour** (11 points over 3.561h, run-state, ceremony included). This is the planning number - points per SESSION within the observed single-session envelope; it is NOT a linear per-point rate to extrapolate to a 1-point or 100-point sprint, and it is descriptive, never a target.

  secondary (points/worker-hour): UNMEASURED - no runner worker-time records (an interactive sprint has none).
Unmeasured: US0433, US0434, US0435, US0436. They are excluded from the batch ratio - an unmeasured unit is not evidence that the estimate was right.
No unit in this batch is rated, so this sprint says nothing about the estimator's accuracy.

Forecast by `TOKENS_PER_POINT=25000`, recorded at plan time. OUT-OF-SAMPLE: forecast by the constants in force, on a sprint they were not fitted to. This is the only kind of row that tells you anything.

Ratio is estimate / actual: above 1 the plan over-forecast, below 1 it under-forecast. Nothing is re-fitted here - see VELOCITY.md for the trend across sprints, and change the constants only on evidence a human has looked at.
<!-- accuracy:end -->

- Not-yet-captured: the interactive-sprint token capture runs at `sprint close --apply-signoff`; this row fills then. The batch was 11 points (US0433 3, US0434 3, US0435 2, US0436 3).

## Actions raised

**Are there any CRs or Bugs you want to raise in this project to address any of the
issues found?**

This is the question that turns a retro into work. Every finding gets a disposition:
**file it** (a BG/CR id), **record it fixed in-sprint** (`fixed-in: <sha or unit>`), or
**decline it with a reason**. All three are green. What does not pass is silence - a
finding written down and left to rot.

| Finding | Disposition |
| --- | --- |
| MINOR-2: the growing-set offer dangled `--file-and-close` at hard `gate` blockers it would refuse | fixed-in: e0529b51 |
| MINOR-1: record-based currency is an honesty gate, not adversarial-proof - a hand-written future-dated `.local/review-state.json` passes the lane | declined: matches the trust model CR0421 requested ("compare against the review record"); the file is gitignored/per-machine and already trusted by `review_prep.staleness`; escalating it to an adversarial gate is a separate design question, not this CR's scope |
| MINOR-3: US0436 AC2's "the two checkers agree" holds only in the safe direction (lane more lenient when anchor-current/record-stale) | declined: the specific opposite-verdict bug the CR named is fixed and tested; the residual disagreement is the lane being more lenient, never more strict, so it cannot pass a genuinely-stale review the checker would flag |
| NIT: `add_to_batch` normalises the whole batch while `drop_from_batch` preserves survivors verbatim | declined: cosmetic; both feed `norm_id`-based readers, no behavioural difference |

## Close loop (gated)

`gate --require-retro RETRO0074` (this retro's id, file form) fails until all four are true:

- [ ] this retro exists AND passes its content check - required sections, at least one real
      lesson, and every finding dispositioned (`retro.py validate --id RETRO0074`)
- [ ] its lessons are in the project store, not just in this file (`retro.py extract --id RETRO0074`)
- [ ] open lessons re-validated: each is closed, extended, or within its horizon (`lessons revalidate`)
- [ ] `retros/LESSONS-SUMMARY.md` regenerated from the still-valid lessons (`lessons summary`)

The next sprint reads them automatically: `sprint plan` prints the digest in the plan.

## Metrics

- Tokens: not-yet-captured (interactive; captured at apply-signoff) · Duration: interactive · Critic rejects: 0 (APPROVE round 1; 1 MINOR fixed, 3 declined with reason)

## Handoff

- [HO-0029](../handoffs/HO0029-deliver-cr0421-a-sprint-close-can-converge-batch.md) - 4 remaining item(s): 0 copilot-tail, 4 judgement. Pick up with `sprint plan --worklist sdlc-studio/.local/handoff-worklist.txt`.
