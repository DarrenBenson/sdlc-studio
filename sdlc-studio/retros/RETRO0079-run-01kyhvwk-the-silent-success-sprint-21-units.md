# RETRO-0079: RUN-01KYHVWK: the silent-success sprint - 21 units, gates that now fail loud

> **Date:** 2026-07-27
> **Batch:** RUN-01KYHVWK - 21 units (16 bugs, 5 stories), 70 points
> **Goal:** Every gate the audit showed silently standing down or silently passing fails loud, and no terminal artefact carries a claim its own verifier contradicts
> **Delivered:** 21 / 21   **Blocked:** 0

## Delivered

- **BG0305** - `parse_story` closed a fence on any three-character run, so inside a four-backtick
  block an inner opener CLOSED the fence and an illustrative Verify line became AC1's executed
  verifier. Reproduced returning a live injected shell command. The mirror harm was quieter and
  worse: a real Verify line after the illustration was swallowed and its AC silently lost its
  verifier. Ported the fence rule the status tool already had.
- **BG0317** - an all-skipped pytest run exits 0 without printing "no tests ran", so an acceptance
  criterion was stamped green by a test that never executed. The batch path had always refused the
  same run, so one run produced two opposite verdicts depending on which path read it.
- **BG0316, BG0314, BG0315** - the Done gate now refuses an AC carrying no Verify line at all
  (omission had been cheaper than honest declaration), a forced bypass is actually recorded, and a
  one-call close pre-flights before it writes.
- **BG0302, BG0303, BG0304** - the conformance threshold restored to 82, four Done stories whose
  verifiers pointed at renamed or deleted tests repaired, and the placeholder sweep widened from
  the acceptance-criteria section to the whole body.
- **BG0321-BG0326, BG0329** - seven more instances of one class: a tool reporting success it did
  not achieve. A gh failure read as "no merged PRs", a crashed checker read as "every unit ready",
  a dangling symlink reported "synced", an unreadable artefact reported clean, a failed remote
  query silently minting a colliding id.
- **US0447-US0451** (EP0166) - the persona registry became load-bearing: a shared reader, the
  mandated creation path resolving through it, the three minting paths proven to agree, and the PRD
  and legacy appendix corrected. `review_prep` now reports personas unused=0.

## Blocked / deferred

- None. All 21 units delivered.

## What went well

- **Eight file-disjoint lanes worked.** The tool's own `--export-lanes` produced the partition and
  it held: no lane collided with another, and the one genuine collision cluster (three bugs all
  changing the status tool) was kept in a single lane deliberately.
- **Three fixes bit their own repository on the way in.** The new Done gate refused two
  long-standing test fixtures; the widened placeholder sweep found 62 findings across 31 terminal
  artefacts; the engagement floor refused the whole batch for carrying no plan. Every one was the
  system working on its author, which is the strongest evidence available that the fixes are real.
- **Reproduce-before-fixing was worth mandating.** Agents were told to return 'already-correct' if
  measurement contradicted the artefact, because two units earlier in the day had rested on
  premises that measurement falsified.

## What was hard / what stalled

- **Eight individually-green lanes still broke the suite.** Every agent reported its own tests
  passing; the full run found two errors neither could have seen, because the defect was
  cross-lane - one lane changed a RULE and another lane's fixtures were built on the old one. An
  agent's self-report is not evidence, and per-lane green says nothing about the whole.
- **The widened check blocked the commit on debt it had just revealed.** 62 pre-existing findings
  turned a previously-green gate red. Reverting the widening would have been the easy answer and
  the wrong one.
- **A bug's `Verify:` line is executed by nothing.** Giving the 16 bugs acceptance criteria to
  satisfy the engagement floor added 15 pseudo-verify warnings on the first attempt - growing the
  exact backlog another unit in the same backlog exists to stop.

## Lessons

- **A widened check must not block on the backlog it reveals.** Widening the placeholder sweep was
  correct and immediately surfaced 31 already-terminal artefacts carrying unfilled scaffolds. A
  check that starts erroring on pre-existing debt gets reverted, which loses the widening too. The
  answer is a baseline captured from the checker's own output - not a hand-written list - that
  downgrades the known set and errors on anything new, with removal one-way so the count can only
  fall. Recorded as project debt rather than quietly tolerated.
- **Per-lane green is not suite green.** Parallel file-disjoint delivery removes file collisions,
  not semantic ones: a lane that changes a rule breaks fixtures owned by lanes that never touched
  its files. Run the whole suite before believing a fan-out.
- **Put the evidence where the tooling actually reads it.** A `Verify:` line on a bug executes
  nothing - only a story's does. Recording the proof under a different marker kept the evidence
  and avoided inflating a warning backlog by 15 in the act of satisfying a different gate.
- **The strongest evidence a fail-loud fix works is that it refuses its own repository.** Three did.

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

- The batch was sized at 70 points before delivery and no unit was re-sized during it, so the
  estimate held at batch level. What the plan did NOT price was the work the fixes themselves
  revealed: the placeholder baseline, its test, and the acceptance criteria the engagement floor
  demanded for 16 bugs were all unplanned and all necessary. A fail-loud sprint generates work by
  succeeding, and that is not a sizing error to correct - it is a property to expect.

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
| 31 terminal artefacts carry an unfilled body scaffold, 12 of them bugs with no symptom, steps or fix | BG0347 |
| The same naive fence toggle survives in the shared parser, the filer, the persona resolver and the link checker | declined: only the verify_ac copy feeds shell execution, so it was the dangerous one; the shared parser is the widest and is worth its own unit |
| The all-skipped hole survives for jest/vitest, unittest and go runners | declined: BG0317's scope was the pytest path; the sibling runner grammars differ enough to need their own unit |
| Two test fixtures were built on the pre-fix permissive Done gate | fixed-in: this sprint - the helper now substitutes an honestly-declared manual verifier |
| A bug's `Verify:` line is executed by nothing, so bug acceptance criteria inflate the pseudo-verify backlog | fixed-in: this sprint - the proof is recorded under a `Proven by` marker instead |

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

- Tokens: captured at close from the harness-tracked delta against this run's baseline · Duration: ~35 min of
  delivery fan-out across 8 lanes · Critic rejects: recorded with the review verdict

## Handoff

- [HO-0033](../handoffs/HO0033-every-gate-the-audit-showed-silently-standing-down.md) - 5 remaining item(s): 0 copilot-tail, 5 judgement. Pick up with `sprint plan --worklist sdlc-studio/.local/handoff-worklist.txt`.
