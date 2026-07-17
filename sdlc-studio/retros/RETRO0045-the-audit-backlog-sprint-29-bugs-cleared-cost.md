# RETRO-0045: The audit-backlog sprint: 29 bugs cleared, cost/measurement machinery made honest

> **Date:** 2026-07-17
> **Batch:** BG0152, BG0153, BG0154, BG0155, BG0156, BG0157, BG0158, BG0159, BG0160, BG0161, BG0162, BG0163, BG0164, BG0165, BG0166, BG0167, BG0168, BG0169, BG0170, BG0171, BG0172, BG0173, BG0174, BG0175, BG0176, BG0178, BG0179, BG0180, BG0181 (the 2026-07-16 adversarial-audit backlog, RUN-01KXQH64)
> **Goal:** Clear the 2026-07-16 audit backlog so the sprint machinery (telemetry, retro, gate) and the documents of record (PRD/TRD/TSD) match the shipped behaviour.
> **Delivered:** 29 / 29   **Blocked:** 0

## Delivered

- **Cluster A - cost/measurement machinery (8, author-driven, shared telemetry/retro/config):**
  BG0152 per-attempt telemetry writer; BG0153 cross-record cost aggregation (rework sums, accuracy
  attempts-first agrees with unit_cost); BG0158 majority run-state elapsed match + explicit override;
  BG0159 pricing by raw model-id (no dot-split); BG0160 config degrades on malformed YAML; BG0164
  attempts-only Delivered-by stamp; BG0165 multi-model unit is MODEL_MIXED (refuses pooled ratio);
  BG0181 batch line strips provenance parentheticals in place.
- **Cluster B - gate + PRD/TRD (7, isolated worktree):** BG0154 atomic + locked decisions ledger;
  BG0155 corrupt close-down baseline is a loud refusal not a silent disarm; BG0166 all three
  retro/lessons lanes honour the opt-out; BG0171 honest `--require-close` help; BG0156/0157/0168
  PRD/TRD/epic spec-rot corrected.
- **Cluster C - TSD (3, isolated worktree):** BG0167 eval gate fails on wholly-ungraded scenarios;
  BG0162/0170 TSD test-coverage + gate-lane tables match the code.
- **Loose (11, isolated worktree):** BG0163 sprint batch-triage reports unreadable drops; BG0175
  review scaffold stamps Raised-by/author; BG0176 migrate stops advising re-size of terminal units;
  BG0178/0179 no MD026 trailing punctuation; BG0180 mutation refuses a red baseline and restores
  stranded mutants; BG0161/0169/0172/0173/0174 doc/record fixes (RFC outcomes, supersession,
  test-spec index, refute quorum, `audit` catalogued).

## Blocked / deferred

- None blocked. Deferred to follow-ups (see Actions raised): the `audit` import-coverage rider
  (BG0162), `help/mutation.md` drift from BG0180, and the gate mutation lane not surfacing the new
  `refused` state.

## What went well

- **File-disjoint fan-out worked.** After the correctness-critical cluster A was done by hand, the
  three remaining file-disjoint groups ran as parallel isolated-worktree subagents (7 + 3 + 11 bugs)
  and merged with zero conflicts - because scope was checked (`git show <commit> --name-only`) rather
  than trusted, and the shared bug index + CHANGELOG were kept off the subagents' hands and applied
  centrally.
- **Every fix was seen red first.** Each bug got a test reproducing the defect before the fix, so a
  green suite means the defect is actually gone, not that the test was written to the fixed code.
- **The closing adversarial review paid for itself** - it caught a real regression the fix's own
  test missed (see below).

## What was hard / what stalled

- **A doc-coverage miss masqueraded as 118 non-conformant units.** BG0174 added `audit` to the Type
  Reference but not the help catalogue; the `documented` conformance stage is a GLOBAL floor, so one
  uncatalogued command failed it for every unit and the paperwork commit was blocked until the
  help/help.md row was added.
- **The bounded mutation run was uninformative** (10 of 826 mutants, all on peripheral git/path
  helpers, 10 survived) - a low ceiling on a large multi-function file samples the wrong lines. The
  assurance for this sprint is the TDD-red-first tests and the adversarial review, not the mutation
  sample; recorded honestly rather than dressed up.

## Critic loop, observed

The closing CODE leg was an independent worktree-isolated reviewer, refute-framed, QA-seat lens,
reading the whole `96bbaa4..HEAD` diff and required to run a reproduction for every claim.

- **1 MAJOR, confirmed and repaired.** BG0181's first fix (`line.split("(", 1)[0]`) truncated the
  batch line at the first parenthesis, silently dropping delivery units listed after an *inline*
  provenance parenthetical (the reviewer's repro: RETRO0006 returned 3 of 8 units). Repaired
  test-first - strip each `(...)` in place with a regex, add a mid-line-parenthetical regression
  test - and re-verified by re-running the reviewer's exact RETRO0006 reproduction (now 8/8).
- **1 MINOR, accepted by design.** Mixed-model units are in the batch `actual_tokens` total but
  excluded from the per-model rows, so the per-model rows do not sum to the batch total. This is
  correct - a mixed unit's tokens cannot be booked to one model's rate - and no code asserts the
  reconciliation; noted, not changed.
- **Everything else held under attack.** The reviewer tried hardest to break the cluster-A cost
  aggregation (double-count on reopen-reclose/bare-close, flat-vs-attempts disagreement, model-only
  records), the majority elapsed-match boundary, the pricing raw-id resolution, and the fail-closed
  paths (BG0155/0167/0180/0154) - all reproduced as sound.

## Lessons

- A fix's test must exercise the failure mode the fix could *introduce*, not only the one it removes:
  BG0181's fix passed its trailing-parenthetical test while silently dropping units after a mid-line
  one - trading harmless over-reporting for worse silent under-reporting. See [[review-model-two-roles]].
- The `documented` conformance stage is a GLOBAL floor: one uncatalogued command fails it for every
  unit. A command added to the Type Reference must also land in the help catalogue, or the whole gate
  reads as 100+ non-conformant units.
- A worktree subagent branches from a base SHA, so `git diff main..branch` shows the other side
  "reverted" and misleads; a three-way merge is still clean when the groups are file-disjoint. Verify
  scope with `git show <commit> --name-only`, not the full-tree diff.
- A bounded mutation run with a low ceiling on a large multi-function file samples early-file lines
  (peripheral helpers), not the diff - uninformative unless line-targeted. Record the sample honestly
  (`N/M enumerated`), never as clean coverage.

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
| BG0152 | 3 | 75,000 | - | **UNMEASURED** (no telemetry token record) | - | - | - | claude-opus-4-8 |
| BG0153 | 3 | 75,000 | - | **UNMEASURED** (no telemetry token record) | - | - | - | claude-opus-4-8 |
| BG0154 | 3 | 75,000 | - | **UNMEASURED** (no telemetry token record) | - | - | - | claude-opus-4-8 |
| BG0155 | 3 | 75,000 | - | **UNMEASURED** (no telemetry token record) | - | - | - | claude-opus-4-8 |
| BG0156 | 1 | 25,000 | - | **UNMEASURED** (no telemetry token record) | - | - | - | claude-opus-4-8 |
| BG0157 | 1 | 25,000 | - | **UNMEASURED** (no telemetry token record) | - | - | - | claude-opus-4-8 |
| BG0158 | 2 | 50,000 | - | **UNMEASURED** (no telemetry token record) | - | - | - | claude-opus-4-8 |
| BG0159 | 2 | 50,000 | - | **UNMEASURED** (no telemetry token record) | - | - | - | claude-opus-4-8 |
| BG0160 | 1 | 25,000 | - | **UNMEASURED** (no telemetry token record) | - | - | - | claude-opus-4-8 |
| BG0161 | 2 | 50,000 | - | **UNMEASURED** (no telemetry token record) | - | - | - | claude-opus-4-8 |
| BG0162 | 2 | 50,000 | - | **UNMEASURED** (no telemetry token record) | - | - | - | claude-opus-4-8 |
| BG0163 | 1 | 25,000 | - | **UNMEASURED** (no telemetry token record) | - | - | - | claude-opus-4-8 |
| BG0164 | 1 | 25,000 | - | **UNMEASURED** (no telemetry token record) | - | - | - | claude-opus-4-8 |
| BG0165 | 2 | 50,000 | - | **UNMEASURED** (no telemetry token record) | - | - | - | claude-opus-4-8 |
| BG0166 | 2 | 50,000 | - | **UNMEASURED** (no telemetry token record) | - | - | - | claude-opus-4-8 |
| BG0167 | 2 | 50,000 | - | **UNMEASURED** (no telemetry token record) | - | - | - | claude-opus-4-8 |
| BG0168 | 1 | 25,000 | - | **UNMEASURED** (no telemetry token record) | - | - | - | claude-opus-4-8 |
| BG0169 | 1 | 25,000 | - | **UNMEASURED** (no telemetry token record) | - | - | - | claude-opus-4-8 |
| BG0170 | 1 | 25,000 | - | **UNMEASURED** (no telemetry token record) | - | - | - | claude-opus-4-8 |
| BG0171 | 1 | 25,000 | - | **UNMEASURED** (no telemetry token record) | - | - | - | claude-opus-4-8 |
| BG0172 | 1 | 25,000 | - | **UNMEASURED** (no telemetry token record) | - | - | - | claude-opus-4-8 |
| BG0173 | 2 | 50,000 | - | **UNMEASURED** (no telemetry token record) | - | - | - | claude-opus-4-8 |
| BG0174 | 1 | 25,000 | - | **UNMEASURED** (no telemetry token record) | - | - | - | claude-opus-4-8 |
| BG0175 | 1 | 25,000 | - | **UNMEASURED** (no telemetry token record) | - | - | - | claude-opus-4-8 |
| BG0176 | 2 | 50,000 | - | **UNMEASURED** (no telemetry token record) | - | - | - | claude-opus-4-8 |
| BG0178 | 1 | 25,000 | - | **UNMEASURED** (no telemetry token record) | - | - | - | claude-opus-4-8 |
| BG0179 | 1 | 25,000 | - | **UNMEASURED** (no telemetry token record) | - | - | - | claude-opus-4-8 |
| BG0180 | 2 | 50,000 | - | **UNMEASURED** (no telemetry token record) | - | - | - | claude-opus-4-8 |
| BG0181 | 1 | 25,000 | - | **UNMEASURED** (no telemetry token record) | - | - | - | claude-opus-4-8 |
| **Batch (rated units only)** | **0** | **0** | **0** | - | **-** | | **-** | - |

**0 of 29 unit(s) measured; 29 of 29 forecast at plan time.**

**Velocity (points/elapsed-hour): UNMEASURED.** No run-state elapsed for this sprint (an interactive sprint's wall-clock would count operator-away gaps as sprint time). Supply a real elapsed with `accuracy --elapsed-hours H` to record it - descriptive, never a target.

  secondary (points/worker-hour): UNMEASURED - no runner worker-time records (an interactive sprint has none).
Unmeasured: BG0152, BG0153, BG0154, BG0155, BG0156, BG0157, BG0158, BG0159, BG0160, BG0161, BG0162, BG0163, BG0164, BG0165, BG0166, BG0167, BG0168, BG0169, BG0170, BG0171, BG0172, BG0173, BG0174, BG0175, BG0176, BG0178, BG0179, BG0180, BG0181. They are excluded from the batch ratio - an unmeasured unit is not evidence that the estimate was right.
No unit in this batch is rated, so this sprint says nothing about the estimator's accuracy.

Forecast by `-`, recorded at plan time. UNFORECAST: no plan-time forecast was recorded, so there is no prediction to judge. Nothing is re-derived to fill the gap.

Ratio is estimate / actual: above 1 the plan over-forecast, below 1 it under-forecast. Nothing is re-fitted here - see VELOCITY.md for the trend across sprints, and change the constants only on evidence a human has looked at.
<!-- accuracy:end -->

- This was an interactive sprint (no per-unit runner telemetry), so per-unit ratios read UNFORECAST/
  UNMEASURED. The plan recorded a 47-point, ~1.18M-token forecast for the 29 units; the
  harness-tracked sprint total is the honest actual to supply with `accuracy --tokens` once read.

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
| `help/mutation.md` (~L37, L52) still describes pre-BG0180 behaviour (a red baseline records error per mutation) - drifts from the fix | BG0182 (filed) |
| gate.py advisory mutation lane does not surface BG0180's new `refused` state - a refused report reads as 0/0 | CR0336 (filed) |
| BG0162 import-coverage rider (real test coverage for autosprint/xrepo, or a CI sweep) deferred - the TSD now states the honest contract, the coverage gap remains | CR0337 (filed) |
| Mixed-model per-model rows do not sum to the batch total (by design; no code asserts it) | declined: correct by design - a mixed unit's tokens cannot be booked to one model |

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

- Tokens: harness-tracked (interactive; not captured per-unit) · Duration: one session, 2026-07-17 · Critic rejects: 1 MAJOR (BG0181 regression, repaired)
