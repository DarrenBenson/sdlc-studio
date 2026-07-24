# RETRO-0070: Sprint 2 of the three-sprint run - clear the delivery backlog (28 units, 89 points)

> **Date:** 2026-07-24
> **Batch:** BG0269, BG0270, BG0272, BG0273, BG0274, BG0275, BG0276, BG0277, US0354, US0357, US0358, US0361, US0362, US0363, US0372, US0374, US0375, US0377, US0382, US0383, US0384, US0385, US0388, US0389, US0394, US0395, BG0267, BG0268
> **Goal:** Clear the delivery backlog to zero open units, so the v5 release cut that follows has no known-open work behind it.
> **Delivered:** 28 / 28   **Blocked:** 0

## Delivered

- **The gate got faster and honest about it.** Diff-scoped conformance and validate lanes (19.55s to 0.73s, independently re-measured); the commit-message check moved ahead of the expensive suites, so a message refusal costs 33s instead of 212s.
- **The parallel-delivery machinery grew teeth.** The scrub sweep is anchored to the repo (it had been skipping entire trees from a worktree, a vacuous pass); a conflicted merge can be committed through the gate again; the delivery contract now names workspace isolation and build-tooling coupling, neither of which produces the merge conflict the file-disjointness check predicts.
- **Measurement replaced assertion in three places.** A root census measured 64 scripts declaring `--root` where the story said 62 and grooming guessed 20 unanchored; a substitution-fingerprint detector reports a MEASURED 3-of-4 catch rate with the fourth named undetectable in principle; the forecast stopped pricing a design rung as a build.
- **The close learned to describe the state it leaves.** A successful close refreshes the review anchor; the seat brief describes the batch it is given rather than the last one planned; a themed batch is no longer reported as unachievable.

## Blocked / deferred

- None blocked. Seven frictions raised mid-sprint carry to Sprint 3: BG0282 (59 scripts still resolve `--root` bare), BG0283 (the inflight guard has no staleness notion), BG0284 (supersession needs a principal-authorised path), CR0413-CR0417.

## What went well

- **The closing review earned the whole sprint.** Five reviewers over disjoint slices found 14 MAJOR/HIGH defects, every one reproduced. Two were severe: a complete BYPASS of the two-role gate, and an artefact gate that passed everything.
- **Mutation testing caught what green suites could not**, repeatedly and at the call site rather than in the function body. Deleting `review-anchor` from the close chain left 4,237 tests green; deleting the post-transition conformance call left three passing tests untouched.
- **Agents reported honestly.** Three independently hit the same inherited red gate, proved it pre-existing by stashing their diffs, and said so. Several recorded surviving mutants as equivalent WITH the reason rather than deleting the guard to make them die.

## What was hard / what stalled

- **An acceptance criterion specified a vulnerability.** US0375's AC said the sign-off gate should ignore a superseded row; a passing test asserted that as a requirement; the result was a complete bypass of the independence gate. The AC was corrected, not met - a new failure mode for this project, and worse than a bug under a correct spec.
- **My repair created the failure it was fixing, inverted.** Reordering the plan writes so a REFUSED plan leaves nothing meant any fault AFTER `open_run` left a live run with no goal, blocking every later plan. And the test I wrote for it patched the ordering that was already safe.
- **A speedup disabled the gate everywhere.** Diff scoping bound to `DEFAULT_CHECKS` meant CI, deploy preflight and close preflight judged zero units on a clean tree. A story committed with `Status: Bananas` passed.
- **Parallel delivery cost real time.** A review agent ran `git checkout` on a file this session was editing; agents shared one scratchpad and a commit landed carrying another agent's subject; a census went stale because a sibling branch merged after it.

## Lessons

- **An acceptance criterion can specify a vulnerability, and a passing test will then defend it.** US0375 asked for the sign-off gate to ignore superseded rows; that IS the bypass. When a test asserts a security-relevant behaviour, ask what an adversary gains from it, not only whether it matches the AC.
- **Fixing an ordering defect can create its mirror image.** The BG0268 repair moved `open_run` first and invented the opposite leak. A repair to an ordering must be tested on BOTH sides of the step it moves.
- **Scoping a check to a diff disables it wherever there is no diff.** An empty changed-set is not an empty scope; a clean tree must judge everything, or CI silently judges nothing.

## Estimate vs actual
## Estimate vs actual

**Were the estimates any good?** The plan forecast a token cost per unit; telemetry recorded
what each one actually cost. This section holds the comparison, so the question is asked every
sprint instead of only when someone remembers to ask it.

Generate it: `scripts/retro.py accuracy --id RETRO0070 --write` - it fills the block below from
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
<!-- accuracy:end -->

- The forecast priced 89 points at a measured 50,879/pt from Sprint 1's actuals rather than the 25,000 seed, so the calibration loop closed. The sprint over-ran its plan because the closing review found four times the defects of Sprint 1's - review cost, not build cost, and the forecast prices the build only.

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
| Two-role gate bypassable via verdict supersession | declined: fixed in-sprint under RUN-01KY8M6Q, so no separate artefact; residual principal-authorised path is BG0284 |
| Diff scoping disabled the artefact gate on every clean-tree caller | declined: fixed in-sprint under RUN-01KY8M6Q, so no separate artefact, with the clean-tree case now a mutation-proven test |
| The BG0268 reorder left a live run on any post-open_run fault | declined: fixed in-sprint under RUN-01KY8M6Q, so no separate artefact; the writes are guarded and the run is torn down |
| An unmeasured rung poisoned the forecast log first-record-wins | declined: fixed in-sprint under RUN-01KY8M6Q, so no separate artefact; a rung that prices nothing records nothing |
| capacity_report spent UNMEASURED as 0 and passed the budget | declined: fixed in-sprint under RUN-01KY8M6Q, so no separate artefact; carried as None and reported unjudged |
| artifact.py wrote through a bare --root while measuring as anchored | declined: fixed in-sprint under RUN-01KY8M6Q, so no separate artefact; five scripts resolve once in main() |
| The census record was false at HEAD (5/59 vs a measured 10/54) | declined: corrected in-sprint under RUN-01KY8M6Q, with the call-site-is-not-an-anchor limit stated in the record |
| The close stamped OWED on the close that records the sign-off | declined: fixed in-sprint under RUN-01KY8M6Q, so no separate artefact; the tail re-stamps once units are Done |
| The close's own anchor stamp blocked its next invocation | declined: fixed in-sprint under RUN-01KY8M6Q, so no separate artefact; a diff confined to the machine block is exempt |
| Empty scope leaked whole-repo on a bug-only batch | declined: fixed in-sprint under RUN-01KY8M6Q, so no separate artefact, with the empty list as the discriminating test |
| 59 scripts still resolve --root bare | BG0282 |
| The inflight guard has no staleness notion | BG0283 |
| artifact.py new has no duplicate check | CR0413 |
| The backlog carries work already delivered, and premises never checked | CR0414 |
| Build tooling reads as file-disjoint from everything | CR0415 |
| The floor cannot attribute work a commit message never names | CR0416 |
| A fields-file allows only prose keys, splitting one invocation | CR0417 |
| Supersession is occurrence-blind and retires later matching rows | declined for this sprint: folded into BG0284, which redesigns the path |

<!-- file one with: scripts/file_finding.py · check with: scripts/retro.py dispose --id RETRO0070 -->

## Close loop (gated)

`gate --require-retro RETRO0070` (this retro's id, file form) fails until all four are true:

- [ ] this retro exists AND passes its content check - required sections, at least one real
      lesson, and every finding dispositioned (`retro.py validate --id RETRO0070`)
- [ ] its lessons are in the project store, not just in this file (`retro.py extract --id RETRO0070`)
- [ ] open lessons re-validated: each is closed, extended, or within its horizon (`lessons revalidate`)
- [ ] `retros/LESSONS-SUMMARY.md` regenerated from the still-valid lessons (`lessons summary`)

The next sprint reads them automatically: `sprint plan` prints the digest in the plan.

## Metrics

- Tokens: not-yet-captured (interactive; captured at close) · Duration: interactive session · Critic rejects: 0 unit-level; the sprint-level review returned 14 MAJOR/HIGH findings across five slices, all reproduced, 10 fixed in-sprint
