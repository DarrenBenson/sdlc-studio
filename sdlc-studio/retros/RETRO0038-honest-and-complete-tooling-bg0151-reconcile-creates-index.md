# RETRO-0038: Honest and complete tooling: BG0151 + reconcile-creates-index + audit cost gate + interactive token measurement

> **Date:** 2026-07-15
> **Batch:** BG0151, US0158, US0159, US0160, US0161, US0162 (EP0043/44/45)
> **Goal:** done
> **Delivered:** 6 / 6   **Blocked:** 0

## Delivered

- **BG0151 (5pt) - the old-linking false-positive fix.** `child_parent` now reads the legacy
  `> **Change Request:**` epic->CR link, so `children_of` sees an old-flow-decomposed CR's epics.
  On ../homelab this dropped `discovery_awaiting` 24 -> 16 and `migrate` needs-refine 12 -> 4 (the
  false positives cleared; the remainder genuinely childless).
- **US0158 (5pt) - reconcile creates a missing index.** `reconcile apply` materialises a missing
  pipeline or meta index from its template (`write_empty_index`) and populates it; dry-run reports
  would-create. The `missing-index` drift is now fixable, not just detectable.
- **US0159 (3pt) - the audit cost estimator.** `audit_cost.py` estimates agents/tokens/wall-time
  and flags large vs small, calibrated to the measured reference run (7 lenses -> ~190 agents).
- **US0160 (3pt) - the audit pre-flight gate.** `reference-audit.md` documents presenting the
  estimate and confirming above a threshold before the fan-out.
- **US0161 (3pt) - interactive token measurement.** `accuracy --tokens N` computes a real sprint
  tokens-per-point over the DELIVERED (terminal) units' points - a deterministic velocity for an
  interactive sprint that has no per-unit telemetry.
- **US0162 (3pt) - the doctrine correction.** The retro template, `retro.py` and `reference-retro`
  now say an interactive sprint's tokens are NOT-YET-CAPTURED (supply with `--tokens`), never
  unmeasurable.

## Blocked / deferred

- Nothing blocked. Two big items surfaced this session are captured, NOT built: **RFC0042** (make the
  sprint close-down un-skippable - the homelab agent shipped without a retro because nothing forced
  it) and a DoR/DoD RFC to raise next (operator directive: finish this sprint, then investigate).

## What went well

- **Dogfooding on a real project earned its keep.** Pointing the skill at ../homelab surfaced BG0151
  - a false-positive in a feature shipped two sprints ago that misreports EVERY old-flow project.
  The bug was invisible to the test suite because every fixture used new-style links; a real project
  had old-style links.
- **The honest-split design contained the blast radius.** BG0151's false positives were reporting
  only: `migrate --apply` never acts on needs-refine, so it could not have harmed homelab - a live
  validation of the deterministic-vs-needs-human contract shipped last sprint.
- **The independent review, again, on-theme.** Dani caught that `_delivered_points` counted
  NON-delivered batch units as "delivered" - an over-claim, in a sprint whose whole theme is honest
  measurement. Fixed to count only terminal units; re-review APPROVE.

## What was hard / what stalled

- **The operator corrected a doctrine I had been repeating.** "Tokens UNMEASURED (interactive)" was
  wrong - the harness tracks tokens deterministically (the homelab audit reported ~6.9M). I had
  conflated "the skill's runner telemetry did not capture it" with "unmeasurable". US0161/US0162
  fix it; the lesson is that a silence in one measurement path is not proof the quantity is unknowable.
- **The close-down is mandated but not enforced.** The homelab agent shipped and deployed without a
  retro - not from laziness but because `gate --require-retro` is opt-in and nothing runs it
  automatically. A control that only fires when someone remembers to run it is the exact
  silent-control failure this project keeps fighting (LL0027). Captured as RFC0042.
- **Two rounds of style-lint provenance-tag failures** cost a cycle each - `(CR0278)`/`(BG0151)` in
  scripts and reference docs. A recurring self-inflicted miss; the tags belong in git/CHANGELOG.

## Lessons

- A false negative in a test suite is a fixture-coverage gap, not proof of correctness: BG0151
  shipped because every fixture used the NEW link style, so no test exercised the old-flow linking a
  real consuming project uses. When a feature reads a convention, fixture BOTH conventions - the
  new one you are building and the legacy one real projects still carry.
- A silence in one measurement path is not proof the quantity is unmeasurable. "Interactive =
  UNMEASURED" hardened a telemetry-capture gap into a false claim of unknowability, blocking the
  velocity loop for the exact sprints being run. Name the gap (not-yet-captured), then close it.
- A mandated ceremony with no mechanical enforcement is a silent control - it fires only when
  someone remembers, which under delivery pressure is never. The close-down needs the same
  un-skippable treatment the quality gate got (RFC0042); the machine version of this bug was the
  whole homelab sprint.

## Estimate vs actual

**Not captured by the skill telemetry - but NOT unmeasurable** (the correction this sprint made).
The plan forecast ~550,000 tokens (22 points x the ~25,000 seed). The actual token spend is
deterministic (harness-tracked); this interactive sprint recorded no per-unit actual, so supply the
sprint total with `retro.py accuracy --id RETRO0038 --tokens N --write` to record a real
tokens-per-point over the 22 delivered points. Not-yet-captured, not unknowable.

<!-- accuracy:begin (generated by retro.py accuracy --write) -->
<!-- accuracy:end -->

- The token actual is knowable (harness-tracked); supply it with `--tokens` to close the velocity
  loop for this sprint. This sprint SHIPPED that capability (US0161).

## Actions raised

**Are there any CRs or Bugs you want to raise in this project to address any of the issues found?**

| Finding | Disposition |
| --- | --- |
| Old-flow CRs false-flagged as un-refined (found dogfooding homelab) | closed: BG0151 fixed this sprint (children_of reads the legacy link), verified on homelab + re-review. |
| `_delivered_points` counted non-delivered batch units as delivered (found in review) | declined: no ticket - fixed this sprint (filter to terminal units) + test. |
| audit cost gate over-warned vs its own docs; tokens-without-points was silent (found in review) | declined: no ticket - both fixed this sprint (raised the token threshold; added the no-denominator note) + tests. |
| The sprint close-down is mandated but not mechanically enforced (homelab agent shipped without a retro) | filed: RFC0042 (make the close-down un-skippable) - a future sprint. |
| DoR/DoD as editable per-project artefacts + gates | declined: no ticket yet - raising as its own RFC immediately after this sprint closes, per the operator directive to finish the sprint first. |

<!-- file one with: scripts/file_finding.py -->

## Close loop (gated)

- [x] this retro exists AND passes its content check
- [x] its lessons are in the project store
- [x] open lessons re-validated
- [x] `retros/LESSONS-SUMMARY.md` regenerated

## Metrics

- Tokens: not-yet-captured (harness-tracked; supply with `accuracy --tokens N`) · Duration: one session · Critic rejects: 0 (APPROVE-WITH-NITS first pass; 3 on-theme honesty nits fixed same sprint; re-review APPROVE)
