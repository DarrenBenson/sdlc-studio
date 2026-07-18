# RETRO-0049: The gate and close chain report their own state honestly: freshness is fingerprinted, refusals and skips are named not silent, and a failure is attributed once to its real cause

> **Date:** 2026-07-18
> **Batch:** US0216, US0213, US0219, US0220, US0217, US0215, US0214, BG0190, US0218
> **Goal:** The gate and close chain report their own state honestly: freshness is fingerprinted, refusals and skips are named not silent, and a failure is attributed once to its real cause.
> **Delivered:** 9 / 9   **Blocked:** 0

## Delivered

- US0216 - the gate's mutation lane names a refused red-baseline run instead of rendering its
  all-zero summary as `0/0 mutations killed`, carrying the report's own remedy.
- US0213 - `verify_ac` records an `ac_fingerprint` (each AC's id, title and Verify command) and the
  Done gate compares that instead of file mtime, so a status transition or a revision-history row no
  longer invalidates a correct green. Legacy reports still fall back to mtime.
- US0218 - `mutation.py --since` reads `git diff -U0` and spends the ceiling on changed lines first,
  reporting `diff_mutations` / `diff_applied` / `diff_covered`.
- US0219 - `tools/gate_timing.py` records each suite's wall-time to a bounded history and estimates
  the next run from the median; the hook announces it before paying it.
- US0220 - the docs-only skip is named rather than silent, stating which guards still ran.
- US0217 - a repo-wide conformance failure is attributed once under `globals` instead of charged to
  every judged unit, without enforcing any less.
- US0215 - the review-current lane tells an uncommitted-but-current anchor from a stale one and
  names committing the close paperwork as the remedy.
- US0214 - `review_prep close` writes its own RV index row through the shared meta-index helper.
- BG0190 - the apply-signoff tail derives a parent epic terminal, scoped to the run's own units and
  refusing on any child it cannot read.

## Blocked / deferred

- None. All 9 units reached Done.

## What went well

- **The independent review earned its cost twice.** It REJECTed the sprint on two successive
  rounds, each time with a reproduction it had run against the shipped tree, and each time on a
  defect my own tests passed straight over. Round 3's APPROVE also corrected my characterisation of
  my own fix (the guard I added is belt-and-braces; the unconditional filter does the work).
- **Mutation-checking every unit before claiming it.** Each behaviour was proven by deliberately
  breaking it and watching the test fail. That is what made round 1's finding legible as a genuine
  gap rather than a difference of opinion.
- **The repo's own guards caught my mistakes.** The commit-msg guard demanded `Refs:` trailers on
  multi-id subjects; the style guard stripped provenance tags from a shipped script; the
  repo-hygiene guard caught test classes I had appended below a mid-file `__main__` guard, where
  direct runs would silently drop them.
- **Dogfooding was immediate.** US0219's estimate printed in its own next commit, and the US0220
  skip fired on the review-record commit.

## What was hard / what stalled

- **Every story arrived as a template skeleton.** All eight had `{{placeholder}}` ACs, so grooming
  was the first cost of every unit and none of it was in the 26 points. The points measured the
  code, not the work.
- **The `refine` seeding mis-distributed criteria.** US0219 carried US0220's criterion while US0220
  had no ACs at all; US0214 carried US0215's. Three of eight stories needed a criterion moved to its
  owning story before they could be built.
- **US0217 broke three tests on first attempt** by reporting a global failure that affected no unit,
  newly failing repos that had legitimately passed. Attributing a failure differently turned out to
  be easy to get subtly wrong in the direction of over-reporting.
- **My own test polluted the suite.** Stubbing `doc_coverage.check` mutated the shared module in
  `sys.modules` and leaked into `test_doc_coverage`, failing 7 tests in a file I never touched.

## Lessons

- A helper that SKIPS what it cannot resolve is safe for detection and unsafe for derivation:
  `_breakdown_units` silently drops an unresolvable child, and reusing it to decide completion
  turned "the only child I could read is done" into "all children are done". Before reusing a
  census helper to make a CLAIM, check what it drops.
- Deriving a terminal status is an assertion about work, so it must be scoped to what the run
  actually touched and must refuse on incomplete evidence. "No children" and "no readable children"
  are both different from "all children complete".
- A truthiness guard on a scope filter (`if wanted and ...`) fails open: an empty scope silently
  becomes an unbounded one. Scope filters should be unconditional, with emptiness handled
  explicitly.
- Monkeypatching a module reached through `sys.modules` leaks across the whole test process; patch
  and register the undo together (`addCleanup`) so the two cannot drift apart.
- A `-k` test filter that matches nothing exits 0 having run zero tests, so a renamed class silently
  converts an executable AC into a green no-op (filed BG0193).

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
<!-- accuracy:end -->

- The 26-point forecast (~650,000 tokens at the seed rate) covered implementation only. It missed
  the grooming of eight skeleton stories and two rounds of review repair entirely, so the points
  under-described the work rather than the code. Per-unit token actuals were not captured for this
  interactive run (CR0278 remains open), so the per-unit ratio is not-yet-captured rather than
  unmeasurable - the harness total can be supplied with `accuracy --tokens N`.

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
| The handoff is snapshotted before the apply-signoff cascade, so units the close just finished are reported as remaining | BG0191 |
| `cross-epic-ac` is a bare keyword match and false-positives on a common English word, blocking a correctly-scoped AC | BG0192 |
| A Verify line whose test filter matches nothing passes vacuously (exit 0, zero tests run) | BG0193 |
| `ID_SEARCH_RE` has no trailing-digit boundary, so a 5-digit id truncates to its 4-digit prefix | BG0194 |
| Eight of nine stories arrived as `{{placeholder}}` skeletons, so grooming cost was invisible to the estimate | declined: this is the known consequence of `--goal done` over a Draft backlog, already recorded as a lesson from RUN-01KXR6XS. The fix is to run `--goal design` first, which is a planning choice, not a defect |
| `refine` seeded one story's criteria onto a sibling in three of eight cases | declined: the seeding note explicitly says "redistribute across this epic's stories as you groom them", so this is documented intent rather than a defect. Worth revisiting if it recurs at this rate on the next refined batch |

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

- Tokens: not-yet-captured (interactive run; supply with `retro.py accuracy --tokens N`)
  · Duration: one interactive session · Critic rejects: 2 (both blocking, both repaired and
  re-verified by the same reviewer)
