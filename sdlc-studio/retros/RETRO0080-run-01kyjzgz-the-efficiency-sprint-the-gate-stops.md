# RETRO-0080: RUN-01KYJZGZ: the efficiency sprint - the gate stops charging for work it is not doing

> **Date:** 2026-07-28
> **Batch:** RUN-01KYJZGZ - 33 units (15 stories, 18 bugs), 107 points
> **Goal:** The cost of running the discipline falls below the cost of the work it guards: the suite runs only when the code it tests has changed, and only in full where a wrong answer is expensive
> **Delivered:** 33 / 33   **Blocked:** 0

## Delivered

- **EP0177 US0493-US0496** - the gate stops charging for work it is not doing: a content hash of the
  tracked surface skips a run when nothing changed, selection from the import graph runs what a
  change can reach, full runs are confined to push, release and close, and the gate reports its own
  cost against a budget.
- **US0497-US0499** - the plan-time test strategy now states the execution policy and its cost, is
  persisted with the plan rather than printed and lost, and the close reports execution actuals
  against it. This sprint's own overhead is what made the omission visible.
- **US0500-US0501** - the close stops invalidating itself: an artefact it creates no longer counts
  as an unreviewed change against it, and a retry over an unchanged surface reuses the verdict.
- **US0502-US0505** - the doctrine names the silent-stall failure mode and its detection rule, and
  mutation testing by a delegated reviewer must run in an isolated checkout.
- **US0506-US0507** - a census attributes suite time and count per module, and a test no mutation
  can kill is reported as a removal candidate.
- **18 bugs** - the all-skipped hole for unittest, jest, vitest and go (BG0348); the naive fence
  toggle in four remaining modules (BG0349); three more silent-success and enumerated-id defects.

## Blocked / deferred

- None. All 33 units delivered.

## What went well

- **Eleven lanes, chosen for file-disjointness rather than severity.** Picking the padding bugs so
  they would not collide with the sequential gate work turned a batch the planner had refused to
  parallelise into nine parallel lanes plus two chains.
- **The friction instruction paid for itself immediately.** A lane reported that the surface hash
  could never match; it was right, and that report is the only reason the sprint's headline story
  was not shipped inert.
- **A guard caught a half-applied change.** A lane died mid-flight leaving a partial edit in
  mutation.py, and the existing scrub-site sweep refused it rather than letting it through.

## What was hard / what stalled

- **Four lanes died mid-flight** - three to a transient safety-classifier error, one to a dropped
  connection - taking 12 units with them, and a resumed lane cannot tell a delivered unit from an
  untouched one. One left a partial edit behind. Filed as BG0355.
- **A review slice died and reported nothing**, so 20 units sat unreviewed until a second pass was
  run for them alone. An absent verdict is indistinguishable from a slow one without checking.
- **The author's own repairs introduced three fresh regressions**, including a handover rewrite that
  silently lost its refuse-when-unwritable semantics. Second consecutive sprint where this happened.
- **The false-positive shell-hazard guard cost real time again** (BG0344): six filed artefacts had
  to have their evidence reworded away from what was actually observed before they could be
  committed.

## Lessons

- **A measured proxy is the wrong instrument for "did anything change".** The surface hash was
  computed over the set of files the suites were measured to read, which omitted 233 tracked files;
  editing SKILL.md left the digest byte-identical while three tests went red. Hashing every tracked
  file costs 0.04s against 2,517 files, so the precision bought nothing and the completeness was
  everything. When a cheap complete answer exists, do not build a clever partial one.
- **Ship the wiring in the same unit as the mechanism, or it is inert.** Twice in one sprint a
  correct mechanism reached nothing: the surface hash could never match because a volatile directory
  was in the digest, and the whole selection path was computed by one hook and ignored by the one
  that runs tests. Both were invisible to a green suite and to the author, and both were the same
  defect - a feature whose value never reaches a caller. A unit's acceptance criteria should name
  the caller, not only the function.
- **An empty measurement is an unanswered question, not an answer of "nothing".** 57 of 162 suite
  modules measured an empty read set because a path built from an imported constant is invisible to
  a static reader, and counting that silence as "reaches no tests" excluded the very module a change
  reddened. The safe direction of an unknown is always more work, never less.
- **A review that only reads the diff misses what HEAD has become.** The finding that mattered most
  in the previous sprint was a repair reverted by a later commit, found only by diffing the claim
  against HEAD. Every review brief since carries that instruction.

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
<!-- accuracy:end -->

- The batch was sized at 107 points and delivered without re-sizing, so the estimate held. What it
  did not price, again, was the work the delivery revealed: two inert-mechanism repairs, four
  regressions of the author's own making, and six artefacts whose evidence had to be reworded to
  pass a false-positive guard. A sprint that builds gates generates work by succeeding, and the
  honest response is to expect it rather than to correct the sizing.

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
| The efficiency core was computed by one hook and ignored by the one that runs tests, so both mechanisms were inert in production | fixed-in: cceb6808 |
| The surface hash omitted 233 tracked files, so the skip fired over a change three tests caught | fixed-in: cceb6808 - the surface is now every tracked file |
| A lane can die mid-flight leaving finished code behind a unit still marked Ready, and a restart cannot tell delivered from untouched | BG0355 |
| The constitution lane is 81% of the per-commit artefact gate, and the hook documents that gate as about one second | BG0351 |
| The shell-hazard corpus assertion forced six artefacts' evidence to be reworded away from what was observed | BG0344, raised previously and hit again this sprint |
| Three more places still enumerate the v2 four-digit id, so a ULID unit escapes them | BG0354 |
| pytest cannot collect the scripts and tools suites in one invocation, so no Verify line can span both | BG0352 |
| A review slice died and reported nothing, leaving 20 units unreviewed until a second pass | declined: the detection rule is already recorded as LL0049 and the doctrine work is US0502/US0503 in this same batch |

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

- Tokens: ~2.6M across delivery and review agents · Duration: delivery ~68 min of lane time across
  two attempts · Critic rejects: 1 REJECT on the delivery (9 majors), re-review pending at the time
  of writing
