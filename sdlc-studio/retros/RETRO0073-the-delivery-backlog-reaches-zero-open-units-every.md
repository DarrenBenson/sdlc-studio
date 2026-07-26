# RETRO-0073: The delivery backlog reaches zero open units - every remaining story delivered and every bug fixed, with executable acceptance criteria passing - so v5 can be cut against a backlog that is empty except for the units the release itself gates

> **Date:** 2026-07-26
> **Batch:** US0356, US0370, US0378, US0390, BG0281, BG0278, BG0285, BG0286, BG0290, BG0280, BG0291, BG0292, US0346, US0347, US0355, US0360, US0364, US0365, US0368, US0381, US0386, US0387, US0396, US0397, US0414, US0426, US0429, BG0279, BG0283, BG0287, US0345, US0348, US0349, US0350, US0351, US0352, US0359, US0366, US0367, US0369, US0373, US0376, US0379, US0413, US0415, US0416, US0417, US0418, US0421, US0422, US0424, US0425, US0428, US0430, US0431, BG0284, BG0293, BG0289, BG0288, US0353, US0380, US0419, US0420, US0423, US0427, BG0282
> **Goal:** The delivery backlog reaches zero open units - every remaining story delivered and every bug fixed, with executable acceptance criteria passing - so v5 can be cut against a backlog that is empty except for the units the release itself gates.
> **Delivered:** 66 / 66   **Blocked:** 0

## Delivered

- The whole delivery backlog reached zero open units: 66 units in this run's batch (50 stories +
  16 bugs) all signed off to Done, plus US0432 delivered live, and v5 cut.
- BG0284 - the review-independence machinery: superseding retires a verdict, not the attribution;
  a principal-authorised correction (recorded boundary, non-worker authoriser) is what un-strands
  a mis-filing, and no author-alone sequence clears the gate.
- EP0118 (US0349/350) report-only lane partition; EP0124 (US0359/360) over-appetite recording;
  the three plan-surface message renderers (US0386/387/390); US0418/US0432 the fields-file
  metadata + gate-budget re-declaration.
- Three dogfooding frictions filed and fixed: BG0295 (compose dry-run gate), BG0296 (mutation
  gitignored-worktree scan), CR0420 (gate budget). Plus BG0294/297/298 duplicate-detection.
- The v5 cut: version bump to 5.0.0 across four homes, release_cut.py (changelog cut + tag guard),
  CHANGELOG cut from 126 fragments.

## Blocked / deferred

- Option A of CR0419 (VELOCITY-derived capacity ceiling) deferred; D0064's manual raise (Option B)
  resolved the acute always-OVER symptom. Refilable when there are enough rows to fit against.

## What went well

- The delegated adversarial review (RFC0051, D0059) did its job: a fresh-context subagent probed
  the independence machinery hard - it tried to construct an author-alone laundering sequence and
  could not - APPROVEd, and named four MINOR residuals rather than rubber-stamping. Two of the
  four were fixed before the cut.
- Filing friction as tickets rather than working around it surfaced three real tool defects
  (compose footgun, worktree scan, gate budget) that would otherwise have stayed folklore.

## What was hard / what stalled

- The pre-commit gate runs ~5 minutes (re-budgeted under CR0420); every unit paid that toll.
- Stale `Verify:` references surfaced only at the close's `verify_ac` run: US0427 pointed at a
  test class that never existed (`DelegatedSignoffTests` vs the real `SignoffDelegateTests`),
  US0347 carried a `../../../../` path pytest cannot parse, US0387 named a method the test did
  not use. Each unit read as delivered while its ACs verified nothing.

## Lessons

- **Verify the premise before building the fix.** BG0296 was filed blaming the mutation tool for
  being blind to guard clauses; checking it first disproved that (the tool mutates guards fine)
  and the real defect was a gitignored-worktree scan. A fix built on the filed premise would have
  been a fix for a defect that did not exist.
- **A destructive default must be opt-in.** `changelog compose` folded and DELETED the whole
  pending fragment set by default; run out of habit while adding one fragment it destroyed 115.
  Dry-run by default, consume only on `--apply`.
- **A `Verify:` line is not verified until it is run.** Three delivered units carried `Verify:`
  references to test nodes that did not exist or paths pytest could not parse - invisible until
  the close ran `verify_ac`. Run `verify_ac` at delivery, not only at close, so a broken verifier
  fails the unit that authored it rather than the sprint that closes it.

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
| US0356 | 1 | 52,575 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| US0370 | 1 | 52,575 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| US0378 | 1 | 52,575 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| US0390 | 1 | 52,575 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| BG0281 | 2 | 105,150 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| BG0278 | 3 | 152,637 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| BG0285 | 3 | 157,725 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| BG0286 | 3 | 157,725 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| BG0290 | 3 | 157,725 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| BG0280 | 2 | 105,150 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| BG0291 | 2 | 105,150 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| BG0292 | 2 | 105,150 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| US0346 | 2 | 105,150 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| US0347 | 2 | 105,150 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| US0355 | 2 | 105,150 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| US0360 | 2 | 105,150 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| US0364 | 2 | 105,150 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| US0365 | 2 | 105,150 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| US0368 | 2 | 105,150 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| US0381 | 2 | 105,150 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| US0386 | 2 | 105,150 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| US0387 | 2 | 105,150 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| US0396 | 2 | 105,150 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| US0397 | 2 | 105,150 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| US0414 | 2 | 105,150 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| US0426 | 2 | 105,150 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| US0429 | 2 | 105,150 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| BG0279 | 3 | 157,725 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| BG0283 | 3 | 157,725 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| BG0287 | 3 | 157,725 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| US0345 | 3 | 157,725 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| US0348 | 3 | 157,725 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| US0349 | 3 | 157,725 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| US0350 | 3 | 157,725 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| US0351 | 3 | 157,725 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| US0352 | 3 | 157,725 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| US0359 | 3 | 157,725 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| US0366 | 3 | 157,725 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| US0367 | 3 | 157,725 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| US0369 | 3 | 157,725 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| US0373 | 3 | 157,725 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| US0376 | 3 | 157,725 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| US0379 | 3 | 157,725 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| US0413 | 3 | 157,725 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| US0415 | 3 | 157,725 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| US0416 | 3 | 157,725 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| US0417 | 3 | 157,725 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| US0418 | 3 | 157,725 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| US0421 | 3 | 157,725 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| US0422 | 3 | 157,725 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| US0424 | 3 | 157,725 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| US0425 | 3 | 157,725 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| US0428 | 3 | 157,725 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| US0430 | 3 | 157,725 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| US0431 | 3 | 157,725 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| BG0284 | 5 | 262,875 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| BG0293 | 5 | 262,875 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| BG0289 | 2 | 105,150 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| BG0288 | 5 | 262,875 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| US0353 | 5 | 262,875 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| US0380 | 5 | 262,875 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| US0419 | 5 | 262,875 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| US0420 | 5 | 262,875 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| US0423 | 5 | 262,875 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| US0427 | 5 | 262,875 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| BG0282 | 8 | 420,600 | - | **UNMEASURED** (no telemetry token record) | - | - | - | - |
| **Batch (rated units only)** | **0** | **0** | **0** | - | **-** | | **-** | - |

**0 of 66 unit(s) measured; 66 of 66 forecast at plan time.**

**Velocity: 4.99 points/elapsed-hour** (193 points over 38.649h, run-state, ceremony included). This is the planning number - points per SESSION within the observed single-session envelope; it is NOT a linear per-point rate to extrapolate to a 1-point or 100-point sprint, and it is descriptive, never a target.

  secondary (points/worker-hour): UNMEASURED - no runner worker-time records (an interactive sprint has none).
Unmeasured: US0356, US0370, US0378, US0390, BG0281, BG0278, BG0285, BG0286, BG0290, BG0280, BG0291, BG0292, US0346, US0347, US0355, US0360, US0364, US0365, US0368, US0381, US0386, US0387, US0396, US0397, US0414, US0426, US0429, BG0279, BG0283, BG0287, US0345, US0348, US0349, US0350, US0351, US0352, US0359, US0366, US0367, US0369, US0373, US0376, US0379, US0413, US0415, US0416, US0417, US0418, US0421, US0422, US0424, US0425, US0428, US0430, US0431, BG0284, BG0293, BG0289, BG0288, US0353, US0380, US0419, US0420, US0423, US0427, BG0282. They are excluded from the batch ratio - an unmeasured unit is not evidence that the estimate was right.
No unit in this batch is rated, so this sprint says nothing about the estimator's accuracy.

Forecast by `TOKENS_PER_POINT=25000`, recorded at plan time. OUT-OF-SAMPLE: forecast by the constants in force, on a sprint they were not fitted to. This is the only kind of row that tells you anything.

Ratio is estimate / actual: above 1 the plan over-forecast, below 1 it under-forecast. Nothing is re-fitted here - see VELOCITY.md for the trend across sprints, and change the constants only on evidence a human has looked at.
<!-- accuracy:end -->

- {{what the ratio implies - which units the estimate missed, and why}}

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
| `changelog compose` deletes the whole pending fragment set by default | BG0295 (fixed-in this sprint) |
| mutation test-file scan descends into gitignored worktree copies | BG0296 (fixed-in this sprint) |
| the pre-commit gate budget is stale and fires OVER on every commit | CR0420 / US0432 (fixed-in this sprint) |
| duplicate detection scope diverges between the two entry points (review MINOR) | BG0297 (fixed-in this sprint) |
| resolve_prose_fields hazard-checks in the unsafe direction (review MINOR) | BG0298 (fixed-in this sprint) |
| mutation scan fails open on a git-less host (review MINOR) | declined: best-effort by design - the scan must never break; documented in the code |
| a verdict-only reviewer's attribution can be cleared by a fabricated principal (review MINOR) | declined: no worse than baseline - the gate rests on recorded ids being truthful, which supersession does not weaken |
| three delivered units carried stale/unparseable `Verify:` references (US0347, US0387, US0427) | fixed-in: US0347, US0387, US0427 (repointed to the real tests + clean paths) |
| eight already-Done stories have red environment-dependent verifiers (US0021, US0040, US0042, US0047, US0052, US0070, US0080, US0251) | declined: pre-existing, not this sprint's regression - they need `gh`/coverage/external tools absent here; a separate verifier-hygiene cleanup, out of the v5 scope |

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

- Tokens: not-attributable (interactive, multi-session run - no per-run baseline delta) · Duration: interactive (UNMEASURED) · Critic rejects: 0 (the delegated adversarial review APPROVEd on the first round, with four MINOR advisories)

## Handoff

- [HO-0028](../handoffs/HO0028-the-delivery-backlog-reaches-zero-open-units-every.md) - 50 remaining item(s): 0 copilot-tail, 50 judgement. Pick up with `sprint plan --worklist sdlc-studio/.local/handoff-worklist.txt`.
