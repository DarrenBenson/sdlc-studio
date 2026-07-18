# RETRO-0048: The two-role close chain holds end-to-end: the close ceremony cascades and signs off deterministically, resists the running-run hazard, and a sprint-level review satisfies the per-unit gate

> **Date:** 2026-07-18
> **Batch:** BG0188, US0236, US0237, US0238, US0247, US0248, BG0189
> **Goal:** The two-role close chain holds end-to-end: the close ceremony cascades and signs off deterministically, resists the running-run hazard, and a sprint-level review satisfies the per-unit gate
> **Delivered:** 7 / 7   **Blocked:** 0

## Delivered

- BG0188 (High) - `open_run` now treats a run carrying any close artefact (`sprint_goal_verdict`/`ended_at`/`handoff`) but `outcome=running` as spent and mints a fresh run; a clean running run still accumulates. Closes the hazard in the exact `sprint plan --write` path the sprint plans through.
- BG0189 (Low) - `project_upgrade.CURRENT_SCHEMA` now derives from the single source of truth (`templates/config.yaml` via new `sdlc_md.current_schema()`); the `.version` stamp follows the project's effective/config schema, so a declined v2->v3 switch stays v2. A coherence test pins the three sources together.
- US0236 - `sprint close --apply-signoff --principal "<you>"` fans a recorded approval into per-unit reviewer-of-record sign-offs + Done transitions; story-scoped, refuses without a principal, stops loud at the first refusal.
- US0237 - the apply-signoff tail writes the run's velocity row (`retro accuracy --write`, keyed by retro id) and runs a final reconcile - so a closed sprint no longer depends on a forgotten manual velocity step (the reason RETRO0046/0047 landed with none).
- US0238 - the whole flow is idempotent: a re-run after a mid-cascade stop resumes, skipping already-done+signed units, with no duplicate velocity row or double telemetry.
- US0247 - `critic sprint-review` records one independent full-diff verdict over a batch; conformance's `critiqued` stage reads it as coverage (verdict + two-role evidence halves) for a covered unit with no individual verdict, never overriding a per-unit REJECT.
- US0248 - the close sign-off brief reads a covered unit as reviewed by the sprint pass, not "(no critic verdict recorded)"; the coverage model is documented in `reference-sprint.md`.

## Blocked / deferred

- None. All 7 units delivered.

## What went well

- The batch was a coherent family (the close/gate/sprint-tooling cluster from the 2026-07-16 audit triage), so each unit reused the last one's surface. `--apply-signoff` (US0236-238) was built almost entirely by orchestrating existing primitives (`critic.record_signoff`, `artifact.close`, `transition`, `retro.record_velocity`), not new machinery.
- The sprint dogfooded its own deliverables: the close was run with `--apply-signoff` (US0236) and the CODE leg was recorded as a sprint-level review (US0247), exercising exactly what this sprint built.
- The pre-commit gate caught two real breakages before they landed (a CHANGELOG duplicate-heading MD024, a reference-sprint.md line-budget overflow) - the un-skippable gate earning its cost.

## What was hard / what stalled

- The groomed stories' Verify lines were written with a syntax the verify DSL rejects (backtick-wrapped `python3 -m unittest discover`, `grep -rq`), so the first verify_ac run failed 12/12 ACs. Rewriting to `grep "<pattern>" <file>` (no flags) and `shell cd ... && python3 -m unittest <TestClass>` fixed it.
- BG0189's one-line constant fix surfaced latent stamp logic: `max(_effective_schema, CURRENT_SCHEMA)` was dead code that only behaved because the constant was wrong. Correcting the constant to 3 broke the declined-switch test until the stamp was re-anchored to the project's own effective/config schema.
- The gate runs the full 2854-test suite (~105s) plus checks, so each commit cost ~2.5 min - a real tax on a 8-commit sprint.

## Lessons

- Verify lines must use the DSL verbs (`grep`/`shell`/`pytest`/`file`/`http`/`eval`), never a backtick-wrapped raw `python3 ...`; the `grep` verb takes `pattern file` with NO flags, and a shell command needs an explicit `shell` prefix. A groomed AC with a non-DSL Verify line passes grooming but fails every verify_ac run.
- Correcting a wrong constant can activate dead code that only ever "worked" because the constant was wrong. When a `max(x, CONST)` or `x < CONST` guard exists only to be a no-op, fixing CONST turns it live - re-derive what the guard should actually compare against, do not just change the number.
- Build a close-ceremony feature by orchestrating the existing tested primitives (sign-off, close, transition, velocity), not a parallel path - the feature inherits their gates (AC-verify, independence, idempotent re-close) for free.

## Estimate vs actual

**Were the estimates any good?** The plan forecast a token cost per unit; telemetry recorded
what each one actually cost. This section holds the comparison, so the question is asked every
sprint instead of only when someone remembers to ask it.

Generate it: `scripts/retro.py accuracy --id RETROxxxx --write` - it fills the block below from
the batch's telemetry and appends this sprint's row to `retros/VELOCITY.md`.

A unit with no per-unit telemetry record has its PER-UNIT ratio reported as **UNMEASURED** and
excluded from that ratio - it is never counted as accurate. But the token count itself is NOT
unmeasurable: the harness tracks it deterministically. An INTERACTIVE sprint (no runner) records no
per-unit actual, so supply the harness-tracked sprint total with `accuracy --tokens N` to get a
real sprint tokens-per-point over the delivered points - report it as **not-yet-captured** until you
do, never as if the number were unknowable. That figure is DESCRIPTIVE, never a target (see CR0273).

The forecast is a hypothesis, not a settled calibration. Read the ratio, write down what it
implies, and change the constants only on evidence a human has looked at - a fit to a couple of
sprints fits noise.

<!-- accuracy:begin (generated by retro.py accuracy --write) -->

| Unit | Points | Estimate (plan-time) | Actual | Ratio (est/actual) | Tokens/pt | Size | Wall | Model |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| BG0188 | 3 | 75,000 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| US0236 | 5 | 125,000 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| US0237 | 5 | 125,000 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| US0238 | 3 | 75,000 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| US0247 | 5 | 125,000 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| US0248 | 3 | 75,000 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| BG0189 | 2 | 50,000 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| **Batch (rated units only)** | **0** | **0** | **0** | - | **-** | | **-** | - |

**0 of 7 unit(s) measured; 7 of 7 forecast at plan time.**

**Velocity (points/elapsed-hour): UNMEASURED.** No run-state elapsed for this sprint (an interactive sprint's wall-clock would count operator-away gaps as sprint time). Supply a real elapsed with `accuracy --elapsed-hours H` to record it - descriptive, never a target.

  secondary (points/worker-hour): UNMEASURED - no runner worker-time records (an interactive sprint has none).
Unmeasured: BG0188, US0236, US0237, US0238, US0247, US0248, BG0189. They are excluded from the batch ratio - an unmeasured unit is not evidence that the estimate was right.
No unit in this batch is rated, so this sprint says nothing about the estimator's accuracy.

Forecast by `-`, recorded at plan time. UNFORECAST: no plan-time forecast was recorded, so there is no prediction to judge. Nothing is re-derived to fill the gap.

Ratio is estimate / actual: above 1 the plan over-forecast, below 1 it under-forecast. Nothing is re-fitted here - see VELOCITY.md for the trend across sprints, and change the constants only on evidence a human has looked at.
<!-- accuracy:end -->

- The plan forecast ~650,000 tokens (26 points x ~25,000). Per-unit token actuals are not-yet-captured for this interactive run; the delivered points (7 units, 26 points) are recorded and the sprint token total can be supplied with `accuracy --tokens N` to close the tokens-per-point read.

## Critic loop, observed

The CODE leg of the close was ONE independent adversarial full-diff review over the whole sprint
diff (`e53202a..HEAD`), framed to refute, run by a separate instance that did not write the code -
recorded as a sprint-level verdict (US0247's own mechanism, dogfooded). Findings, refutations and
the survivors of the pass are recorded here and in `reviews/sprint-review-record.md`.

- **Round 1: REJECT (1 BLOCKING).** The pass reproduced a real regression BG0189 introduced: `audit()` still flagged `stale-version` as auto-correctable for any project below `CURRENT_SCHEMA` (now 3), but `apply()` no longer bumps schema to `CURRENT_SCHEMA` - so a legitimately-v2 project got a permanent, uncorrectable false finding, breaking the dry-run==apply honesty invariant. This was invisible to the author: the new coherence test only checked the constant, not `apply()`'s stamp behaviour.
- **Also found (MINOR):** US0247 and US0236 did not compose - `_signoff_author` did not read `sprint_review_for`, so a unit covered only by the sprint-level review could not resolve its author for the sign-off. Plus an independence observation: the sign-off principal could equal the sprint-level reviewer (the per-unit path forbids that).
- **Refuted / survived:** the reviewer mentally reverted each hunk of BG0188 (`_is_spent`), the conformance verdict-half and REJECT-not-overridden guards, and confirmed the new tests catch the reversion (non-vacuous); `_CLOSE_ARTEFACTS` correctly excludes `scaffolded_retro`, so scaffold-then-fill still accumulates.
- **Round 2:** all three repaired in commit 39f346a with tests (audit/apply consistency on a v2 project; author-from-sprint-review; principal != sprint reviewer); re-verification by the same reviewer recorded in `reviews/sprint-review-record.md`. The independent review earned its cost - it caught a shipped regression the author's own tests missed.

## Actions raised

**Are there any CRs or Bugs you want to raise in this project to address any of the
issues found?**

This is the question that turns a retro into work. Every finding gets a disposition:
**file it**, or **decline it with a reason**. Both are green. What does not pass is
silence - a finding written down and left to rot.

To say "nothing worth raising", say so in a row and give the reason. An empty table is
not an answer.

| Finding | Disposition |
| --- | --- |
| Verify-line DSL friction (non-DSL forms pass grooming, fail verify_ac) | declined: captured as a lesson; the verify_ac error already names the DSL verbs and the fix is mechanical, not worth a CR |
| The pre-commit gate runs the full suite per commit (~2.5 min/commit) | declined: the un-skippable full gate is a deliberate trunk-based-CI choice; speeding it is a known trade-off, not a defect |
| BG0189 audit/apply stale-version regression (BLOCKING) | declined: no separate ticket - repaired in-sprint before close (commit 39f346a) with a regression test, not deferred |
| apply-signoff x sprint-review author resolution + principal independence | declined: no separate ticket - repaired in-sprint (commit 39f346a) with tests |
| The coherence-test gap that let the BLOCKING finding through (no test of apply()'s v2 stamp behaviour) | declined: the repair added exactly that test (`AuditApplyConsistencyTests`), closing the gap |

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

- Tokens: ~650,000 forecast (per-unit actuals not-yet-captured) · Duration: interactive session · Critic rejects: 1 (closing sprint-level review, round 1; repaired and re-verified)

## Handoff

- [HO-0006](../handoffs/HO0006-the-two-role-close-chain-holds-end-to.md) - 5 remaining item(s): 0 copilot-tail, 5 judgement. Pick up with `sprint plan --worklist sdlc-studio/.local/handoff-worklist.txt`.
