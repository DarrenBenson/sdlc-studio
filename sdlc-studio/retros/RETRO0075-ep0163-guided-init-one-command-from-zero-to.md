# RETRO-0075: EP0163 guided init - one command from zero to a first sprint plan

> **Date:** 2026-07-27
> **Batch:** US0437, US0438, US0439, US0440, US0441, US0442, US0443, US0444
> **Goal:** Ship guided onboarding: one command walks a new user from zero to a first sprint plan, greenfield and brownfield alike
> **Delivered:** 8 / 8   **Blocked:** 0

## Delivered

- US0437 - the orchestrator skeleton: a resumable `.local/onboarding.json` checkpoint, path classification (greenfield vs brownfield from `detect_stack`), and the stage runner.
- US0438 - the AGENTS.md stage plus the confirm/skip runner (`init guided --confirm` / `--skip`), draft-then-confirm advancing one stage at a time.
- US0439 - the PRD stage, forking greenfield (author from a conversation) vs brownfield (generate from the existing code).
- US0440 - the TRD and TSD stages, generated from the PRD (the TSD also from the detected stack on brownfield), so the plan never reads a document that does not exist.
- US0441 - the personas stage: grow the engineering team from the PRD and its risk signals, to accept or edit.
- US0442 - the decompose and first-plan stages, landing the operator at a ready first sprint plan - onboarding ends where delivery begins.
- US0443 - `status`/`hint` resume the guided flow and name the next stage until the first plan (precedence over the pipeline ladder).
- US0444 - documented `init guided` in the init help; RFC0019 (the earlier greenfield first-mile loop) marked Superseded, its intent now realised and generalised to brownfield.

## Blocked / deferred

- None. Every batch unit reached Done.

## What went well

- Spine-first delivery: each stage built, tested (TDD), mutation-checked and committed on its own, so the flow grew end-to-end without a big-bang integration.
- The independent adversarial review returned APPROVE with no MAJOR and a credible could-not-break list, and its two fixable findings (a mutation-proven TSD coverage gap; a corrupt-state crash on the orientation path) were repaired and re-verified before sign-off.
- The one command finally closes the adoption gap RFC0055 named: a returning v1 user or a newcomer no longer has to know the pipeline order.

## What was hard / what stalled

- The per-commit gate ran the full ~5.5-minute unit suites even for the `help/init.md` docs commit - correctly, because `gate.py --test-relevant` measures from what the suites actually read (help pages and shipped artefacts), not just `scripts/`. Not a defect; worth remembering so a docs commit is budgeted the full window.
- A docs blockquote placed next to the metadata blockquote tripped MD028 (blank line between blockquotes) - the supersession note had to become a plain paragraph.

## Lessons

- A read on the orientation hot path (`status`/`hint`) must never crash on a hand-mangled runtime file: degrade to absent and self-heal. Adding a new reader of a `.local` file silently widens that file's blast radius to every command that reads it.
- A directive assembled from a conditional (brownfield adds "detected stack") needs the NEGATIVE case pinned too - the mutation making it unconditional passed every test until the greenfield-omits-stack assertion was added.

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
**file it** (a BG/CR id), **record it fixed in-sprint** (`fixed-in: <sha or unit>`), or
**decline it with a reason**. All three are green. What does not pass is silence - a
finding written down and left to rot. The three are counted separately at close: a sprint
that repaired eleven findings reads as eleven fixed, not eleven declined.

To say "nothing worth raising", say so in a row and give the reason. An empty table is
not an answer.

| Finding | Disposition |
| --- | --- |
| TSD greenfield stack clause unpinned (mutation-proven coverage gap) | fixed-in: acd2726f |
| Corrupt/shape-invalid onboarding.json crashes status/hint | fixed-in: acd2726f |
| Duplicate Verified line pair in US0443 | fixed-in: acd2726f |
| Onboarding can reach "complete" with zero artefacts | declined: `--confirm` is the operator's word that they did the step; decompose/plan have no doc to check |
| Abandoned-but-incomplete onboarding nags until --reset | declined: by design - a resumable checkpoint; --reset is the documented escape |

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
