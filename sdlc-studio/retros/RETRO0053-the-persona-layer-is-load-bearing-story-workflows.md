# RETRO-0053: The persona layer is load-bearing: story workflows resolve registry-first, the seat cast is grounded in this repo, and validate covers the legacy layout

> **Date:** 2026-07-19
> **Batch:** EP0049, EP0050, EP0051, US0177, US0178, US0179
> **Goal:** The persona layer is load-bearing: story workflows resolve registry-first, the seat cast is grounded in this repo, and validate covers the legacy layout.
> **Delivered:** 6 / 6   **Blocked:** 0
>
> **RECONSTRUCTED.** This sprint shipped on 2026-07-16 in commit `f7866db` and was never closed.
> This retro was written on 2026-07-19, three days later, from the commit body, the artefact files
> and the surrounding git history - not from the run. Treat the Delivered section as evidenced and
> the reflective sections as weaker than a contemporaneous retro: they record what the record
> supports, and say so where it supports nothing.

## Delivered

All six units shipped in a single commit, `f7866db`, on 2026-07-16 at 18:51. The work answered the
weakest leg of the unified review RV0010, which scored the persona pillar at 40 per cent with both
registry personas unused.

- **US0177 / EP0049** (3 pts, CR0283) - story workflows resolve personas registry-first.
  `reference-story.md` create and generate prerequisites read the `personas/` registry, with
  `personas.md` kept as a legacy fallback; selection defaults to the declared Primary, and a Negative
  persona is never a story target. `help/story.md` was brought into agreement.
- **US0178 / EP0050** (2 pts, CR0292) - the seat cast migrated and grounded. `migrate --apply` moved
  the cards from the retired `personas/amigos/` to `personas/seats/`, and the scenarios were
  rewritten from a fictional shopping app to this repo's own ground truth and its actual Primary,
  Maya Okafor. All three seats resolve warning-free.
- **US0179 / EP0051** (2 pts, CR0297) - `validate` covers the legacy layout. `check_personas` now
  gives a `personas.md`-only project a layout advisory plus a light structural check, instead of a
  vacuous clean pass (LL0008). Six new tests, red-then-green.

Evidence recorded in the commit: every AC executable and Verified, seat-critiqued APPROVE times
three, gates green, delivered through the two-backlog discipline (the three CRs refined into
EP0049-0051 / US0177-0179 before any code).

## Blocked / deferred

- None. All six units reached terminal in the one commit.

## What went well

- **The unified review's weakest pillar became a sized batch.** RV0010 scored personas at 40 per
  cent and named the specific defect - both registry personas unused. That reading turned into three
  CRs, three epics and three stories rather than a note, which is the discovery-to-delivery path
  working as designed.
- **The vacuous-pass fix is the durable one.** US0179 replaced a clean pass over a layout the checker
  could not actually read. A checker that returns green on input it does not understand is worse than
  no checker, because it is counted as coverage. This is the same defect class the sprints since have
  kept finding, three days before it was named as one.
- **Grounding the seats in this repo.** Scenarios written against a fictional shopping app cannot
  seat-score this repo's backlog. Rewriting them against actual ground truth is what made the seat
  critiques in later sprints mean anything.

## What was hard / what stalled

- **The record does not say, and I will not invent it.** A reconstruction three days later has the
  commit body and the diff; it does not have the friction. No blockers, refusals or repair rounds are
  recoverable from the evidence, and their absence from the record is not evidence of their absence
  from the run.
- **What is recoverable is the close itself: there wasn't one.** Six units reached terminal and no
  retro was written, so nothing fed the next sprint's lessons digest and `close_owed` carried the
  debt for three days. It was detected on 2026-07-16 by the close-owed detector built that same
  morning (`fa612ce`), reported to the operator, and consciously left. That decision is what this
  retro is now reversing.

## Lessons

- **A detector firing on a real gap is only worth what the response to it is worth.** The close-owed
  detector correctly reported this sprint as unclosed on the day it shipped. The debt then sat for
  three days across four subsequent sprints. Building the instrument is the cheap half.
- **A checker that passes on input it cannot parse reports coverage it does not have** (US0179's
  `personas.md`-only vacuous pass). Prefer an explicit advisory over a silent green.

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

- **Not recoverable, and not counted.** 7 points delivered. No plan-time forecast was recorded for
  this batch and the harness token total for a session three days past is not retrievable now, so
  this sprint contributes no estimate-versus-actual evidence. It is excluded from the calibration
  rather than entered as a guess - a reconstructed number would corrupt the rate every later sprint
  is measured against.

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
| Six units reached terminal with no close, and the debt survived three days and four sprints after the detector reported it | declined: this retro is the fix. The detector already existed and worked; nothing new to build |
| A reconstructed retro cannot supply estimate-versus-actual, so the batch is lost to calibration | declined: correctly excluded rather than guessed. The general problem - interactive sprints having no token actual - is already open as CR0278 |
| The retro was skipped by an explicit operator decision with no record of that decision on the artefacts | declined: superseded. The decision was reversed on 2026-07-19 and this retro records it |

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

- Tokens: not-yet-captured (reconstructed; see Estimate vs actual) · Duration: not recoverable · Critic rejects: 0 recorded (seat critiques APPROVE x3)
