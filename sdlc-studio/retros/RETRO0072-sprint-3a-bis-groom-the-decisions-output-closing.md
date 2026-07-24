# RETRO-0072: Sprint 3a-bis - groom the decisions' output, closing out 3a's partial verdict

> **Date:** 2026-07-24
> **Batch:** US0419, US0420, US0421, US0422, US0423, US0424, US0425, US0426, US0427, US0428, US0429, US0430, US0431
> **Goal:** The 13 stories the operator's four rulings created carry authored acceptance criteria and an executable Verify line, so Sprint 3b can be planned against a fully groomed backlog and the PARTIAL verdict Sprint 3a returned is closed out.
> **Delivered:** 13 / 13   **Blocked:** 0

## Delivered

- **All 13 stories groomed** - 30 acceptance criteria authored, all moved Draft to Ready. These are the delivery units EP0157-EP0160 that the operator's four rulings produced.
- **Red-now ledger: pass=0, fail=30.** The same bar 3a proved, over the units 3a could not reach.
- **conformance reports 0 ungroomed stories** - the first time in this workstream. Sprint 3b can now be planned against a fully groomed 64-unit backlog, which is what 3a's PARTIAL verdict was about.
- **The capacity instrument works again.** D0064 re-derived the ceiling from measured rows, and this plan reported WITHIN BUDGET - the first plan to do so in months.

## Blocked / deferred

- **Nothing blocked.** BG0293 (`gate --release` unrunnable) blocks the v5 cut but not Sprint 3b, and is in 3b's scope.

## What went well

- **Pre-checking the doc anchors cut the vacuous verifiers from three to one.** Before writing the criteria, the four grep targets intended for documentation stories were tested against the shipped files to confirm each was absent.
- **The capacity change proved itself immediately.** A ceiling that had reported OVER BUDGET on every plan for months reported WITHIN BUDGET on a batch that genuinely fits - the signal is a signal again rather than a constant.
- **Every gate that fired was correct.** The goal-review requirement, the themed-batch advice carried as advice, and the done-gate refusing units whose ACs are correctly red.

## What was hard / what stalled

- **The pre-check did not eliminate the vacuous verifier, and could not.** US0426 anchored on `self-reported`, a phrase already at reference-sprint.md:581 describing harness telemetry. The pre-check tested `Ponytail` and both section headings and stopped there - four anchors, three tested. The ledger caught what the pre-check missed, exactly as in 3a.
- **The backlog rose again during the run** - filing BG0293 and CR0419 while grooming. Correct, and worth noticing as a pattern rather than a surprise: every rung of this workstream has ended with more units than it started, because looking closely at machinery is what produces findings.

## Lessons

- **A pre-check is an enumeration, and an enumeration is a lower bound.** Testing the anchors before writing them reduced three vacuous verifiers to one - real value, and not a substitute for the exhaustive check. The pre-check can only test the anchors someone thought of; the ledger tests all of them. Use both, and never let the cheap one create confidence that retires the complete one.
- **A measurement instrument that always reads the same is off, whatever it says.** The capacity ceiling reported OVER BUDGET on every plan for months and nobody read it. One decision made from four measured rows restored the distinction between a batch that fits and one that does not - the fix was not a better warning, it was a threshold anyone had chosen against evidence.

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

- {{what the ratio implies - which units the estimate missed, and why}}

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
| A verifier passed against unbuilt behaviour: US0426 anchored on `self-reported`, already present at reference-sprint.md:581 | declined: fixed in-sprint under RUN-01KYAG6X - re-anchored on `Ponytail` and the reason recorded in the criterion |
| The doc-anchor pre-check tested three of four anchors, so it reduced but did not eliminate vacuous verifiers | declined: inherent to a pre-check, recorded as a lesson rather than a defect - the exhaustive ledger is the control and it worked |
| `gate --release` does not finish inside 10 minutes, blocking the v5 cut on its own terms | BG0293 |
| The capacity ceiling was stale against every sprint in the record | CR0419 |
| CR0355 could not clear before v5 and v5 could not ship before it cleared | declined: resolved as D0063 - a rule marking release-gated units excluded from the emptiness precondition, not a defect |

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

- Tokens: {{tokens}} · Duration: {{duration}} · Critic rejects: {{rejects}}

## Handoff

- [HO-0027](../handoffs/HO0027-the-13-stories-the-operator-s-four-rulings.md) - 13 remaining item(s): 11 copilot-tail, 2 judgement. Pick up with `sprint plan --worklist sdlc-studio/.local/handoff-worklist.txt`.
