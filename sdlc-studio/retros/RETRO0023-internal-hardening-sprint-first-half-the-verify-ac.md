# RETRO-0023: Internal-hardening sprint (first half): the verify_ac and review_prep clusters

> **Date:** 2026-07-14
> **Batch:** BG0125, BG0128, CR0251, BG0129, CR0253
> **Goal:** clear the review findings safe under the freeze + close the review-gate hole
> **Delivered:** 5 / 5   **Blocked:** 0

## Delivered

- BG0125 - grep verifier expands globs; the documented `src/**/*.ts` example no longer false-REDs;
  the verb went from zero tests to covered.
- BG0128 - rg-vs-grep dialect difference documented (POSIX-ERE portability).
- CR0251 - `verify_ac run/lint` accept `--file` as an alias for `--story`.
- BG0129 - `review_prep` no longer miscounts `personas/index.md` as a persona.
- CR0253 (P1) - `gate --require-review`: the sprint-close review is a hard gate now.

## Blocked / deferred

- The sprint's second half (BG0126 meta_new lock, BG0127 atomic_write, CR0248 archive dedupe,
  CR0249 status-vocab, CR0250 security docs) - a deliberate cut, not a blocker. It stays on the
  backlog; the two heavy-file clusters (archive.py, artifact.py) are a natural next sprint.

## What went well

- Cluster-coherent execution held: one agent per shared file (verify_ac.py, then review_prep.py),
  no conflicts, each cluster gated and committed clean.
- Every fix carried a test that fails against the pre-fix behaviour (LL0010). The grep verb had
  zero coverage - the reason its bug survived - and now has the exact false-RED case pinned.
- CR0253 proved itself on delivery: run against its own sprint, the new `--require-review` gate
  correctly flagged this review anchor stale (18 artefacts changed). The hole the operator found is
  closed and self-demonstrating.
- The gates caught three of my own slips mid-sprint: internal `(BGxxxx)` tags in shipped scripts, a
  duplicate CHANGELOG heading, and a bound lane missing from `BLOCKING_ON_ERROR`.

## What was hard / what stalled

- A first test I wrote for the `--file` alias failed for the wrong reason (a relative path that did
  not resolve from the verifier's cwd), not the flag - I had to isolate the flag with an absolute
  path. A test that fails for a reason other than the one it names is a false signal.

## Lessons

- A gate that enforces a ceremony should be run against its own delivery as the acceptance test:
  CR0253 flagging its own sprint's stale review is stronger evidence than any unit test.
- When two code paths express the same filter (`review_prep`'s two persona-index excludes), give
  them one shared definition or they drift - one had `index.md`, both should have (LL0016).

## Estimate vs actual (manual - RFC0034/CR0258 will automate this)

Plan estimate (complexity-informed): ~600-700k true for the two clusters (the planner's ~1.135M
summed over-counted the shared verify_ac.py cluster 3x). Actual: not instrumented - this sprint was
executed by hand, not through the telemetry-logging loop, so there is no recorded token/wall-clock
actual to compare. This is exactly the gap RFC0034 closes: CR0258 will read the telemetry actual
against the plan estimate automatically. First data point once an instrumented sprint runs.

## Actions raised

**Are there any CRs or Bugs you want to raise in this project to address any of the issues found?**

| Finding | Disposition |
| --- | --- |
| The grep verb's shared-file cluster is over-counted by the token forecast (3 units on verify_ac.py summed) | declined: it is the same shared-file-cluster over-count already noted for the planner; belongs to RFC0034's sizing work (CR0257/CR0259), not a new artefact |
| A test that fails for the wrong reason (the `--file` alias repro) nearly masked a real pass | declined: fixed in place this sprint (absolute-path isolation); a habit, not a ticket - captured here as a lesson |
| The sprint's second half is unshipped | BG0126, BG0127, CR0248, CR0249, CR0250 - already filed and on the backlog; next sprint |

## Close loop (gated)

- [x] this retro exists AND passes its content check (`retro.py validate --id RETRO0023`)
- [x] its lessons are in the project store (`retro.py extract --id RETRO0023`)
- [x] open lessons re-validated
- [x] `retros/LESSONS-SUMMARY.md` regenerated
- [x] the review is current (`gate --require-review` - CR0253, this sprint's own new gate)

## Metrics

- Delivered 5/5 · 2 clusters, one agent per file · 2051 tests green · gate green
