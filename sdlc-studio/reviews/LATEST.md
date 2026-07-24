# Reviews - LATEST (anchor)

<!-- close-status:begin -->
> **RUN-01KY8M6Q closed goal-reached.** 28 unit(s) in the batch. **Sign-off is OWED and is the operator's** - the two-role gate holds Done.
> Stamped by `sprint close` - edit the prose below, not this block.
<!-- close-status:end -->

> **RUN-01KY8M6Q (Sprint 2 of the three-sprint run) delivered all 28 units, 89 points.** The
> closing review found 14 MAJOR/HIGH defects across five slices, every one reproduced; ten were
> repaired in-sprint and the residue is filed. Goal ACHIEVED. Sign-off applied by the operator.

## Where the pipeline is (2026-07-24)

Sprint 2 of three is CLOSED and SIGNED OFF. 18 stories Done, 10 bugs Fixed, 10 parent epics and
10 change requests derived terminal from their children. The delivery backlog reached zero open
units, which was the goal, so the v5 release cut has no known-open work behind it. Sprint 3
carries the ungroomed story skeletons, the frictions raised here, and EP0117 (the cut itself).

The close itself needed hand-work in three places, all filed: `--apply-signoff` fans into story
units only and left the batch's 10 bugs Open while reporting goal-reached (BG0286); the review
anchor goes stale against the close's own transitions, so the lane guarding currency blocks the
step that would refresh it (BG0287, filed after hitting it three times in a row); and
all-manual-AC stories are left non-conformant by the automated verify pass, since `verify_ac`
will not annotate them. BG0285 records a fourth, with its diagnosis marked unconfirmed.

## What shipped

- **The gate got faster and stayed honest.** Diff-scoped conformance and validate (19.55s to
  0.73s, re-measured independently); the commit-message check now precedes the expensive suites,
  so a message refusal costs 33s rather than 212s.
- **Parallel delivery grew teeth.** The scrub sweep is anchored to the repo (it had been skipping
  whole trees from a worktree - a vacuous pass); a conflicted merge is committable again; the
  delivery contract names workspace isolation and build-tooling coupling.
- **Measurement replaced assertion.** A root census measured 64 scripts declaring `--root` where
  the story asserted 62 and grooming guessed 20 unanchored; the substitution detector reports a
  measured 3-of-4 catch rate with the fourth named undetectable in principle.
- **The close describes the state it leaves.** The anchor refreshes on a successful close and is
  re-stamped once sign-offs land; the seat brief describes the batch it is given; a themed batch
  is no longer reported as unachievable.

## The closing review

Five reviewers over disjoint slices. Two findings were severe. A complete **bypass of the
two-role gate**: an author could supersede the verdict blocking them and sign off through their
own subagent - and US0375's acceptance criterion had SPECIFIED that behaviour, with a passing
test defending it. And an **artefact gate that passed everything**: diff scoping bound to every
caller meant CI, deploy preflight and close preflight judged zero units on a clean tree, so a
story committed with `Status: Bananas` gave `gate: PASS`.

Both are closed and mutation-proven. The residue is BG0282-BG0285 and CR0413-CR0417.

US0375 is the one to read. Its AC1 had *specified* the bypass, so the story, the test and the code
all agreed with each other and were all wrong together. Closing it meant amending the acceptance
criterion, not just the code - the record now states the inverted rule and says why it changed.

## Evidence

4241 skill tests + 353 tool tests green, every repo guard clean, drift 0, noise at baseline.

## Next steps

- **Sprint 3**: the ungroomed skeletons (~77 pts), this sprint's frictions, then EP0117 - the
  v5 cut itself.
- **BG0284 is the one to read first**: closing the gate bypass left the mis-attributed-reviewer
  case unsolved, and it needs a principal-authorised correction path.

## Lessons

An acceptance criterion can specify a vulnerability, and a passing test will then defend it.
Fixing an ordering defect can create its mirror image. Scoping a check to a diff disables it
wherever there is no diff.
