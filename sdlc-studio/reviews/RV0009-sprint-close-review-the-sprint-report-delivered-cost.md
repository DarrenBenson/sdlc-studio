# RV-0009: Sprint-close review - the sprint report: delivered, cost, velocity (RFC0035 -> EP0048)

> **Date:** 2026-07-16
> **Created-by:** sdlc-studio new
> **Review type:** Sprint-close review (required by the `--require-review` gate)
> **Reviewer of record:** Darren Benson (operator) - signed off explicitly; adversarial pass by the Dani Okafor engineering seat (subagent)
> **Provenance:** preserved verbatim from `reviews/LATEST.md` before the 2026-07-16 unified review (RV0010) overwrote that anchor. LATEST.md is a stable pointer, not a record; this file is the record.

## Scope

The RFC0035 -> EP0048 sprint: `sprint_report.py show` plus the estimator-core support
(per-attempt telemetry, true cost with rework, points-per-elapsed-sprint velocity,
config-gated rendering). Project version 4.1.0 released; unreleased work on `main`
under a freeze until ~2026-07-21.

## Findings

**5/5 delivered (20 points).** RFC0035 built and Accepted, ABSORBING CR0273 (Superseded). New
`sprint_report.py show` composes - deterministically, at no model-token cost - what a sprint
delivered, what it cost, and whether the estimate held. Estimator-core support, all additive and
honesty-guarded: **per-attempt telemetry** (an `attempts` list; a legacy record reads as one attempt,
no migration), **true cost with rework** (`unit_cost` sums over attempts, priced offline from
`pricing.*`; unpriced models named not guessed), **points-per-elapsed-sprint velocity** (from CR0273;
ceremony included, descriptive, fed to no gate), and **rendering gated by config while recording is
never gated**. Full suite 2553, 0 drift, style clean.

### The review this sprint (estimator core - the highest-scrutiny subsystem)

The Dani Okafor engineering-seat subagent ran the adversarial pass and returned **REQUEST-CHANGES**
with **three MAJORs in the cost-honesty path**, then **APPROVE** once fixed:

- a tokens-only attempt crashed the report render (a `None` model into a `join`);
- a NEGATIVE configured price was honoured and SUBTRACTED from the batch total - a flattering figure,
  the exact class this subsystem exists to prevent;
- the two honest subsystems contradicted - `accuracy` read flat `tokens` while the spend summed
  `attempts`, so an escalation would read UNMEASURED in the ratio while priced in the report.

Plus a foreign-model substring mispricing and an open-run-state elapsed confounder. All fixed with
regression tests that assert the honesty property, not the happy path. The two headline numbers a
reader sees (measured spend, estimate-vs-actual ratio) now draw actual tokens from ONE reconciled
source. The operator signed off as reviewer of record; the subagent cannot record its own verdict
(self-approval guard) - see RFC0044.

### Dogfooding earned its keep before the review

Running `accuracy` on RETRO0040 read 43h of elapsed from a STALE run-state (an old runner run left
open), not this sprint - caught and fixed to require the run-state's batch to name this sprint's
units. The operator-supplied 1.5h gave 13.3 points/elapsed-hour, validating the operator's felt
velocity heuristic.

### Backlog rollup (non-terminal, at sprint close)

- **RFC0036** (rolling multi-sprint policy), **RFC0043** (DoR/DoD, XL - needs a D2 consult),
  **RFC0044** (reviewer roles - build), **CR0279** (read-guard sweep, filed this sprint). Release-gated
  (5.0.0, after the freeze): RFC0040, CR0254/0255/0256, CR0272 retire-half. Non-blocking cleanup: a
  `gitutil` import quirk makes `ProjectStampTests` error under a non-canonical run invocation.

## Verdict

Sprint accepted by the reviewer of record. v4.1.0 released; freeze holds until ~2026-07-21;
all sprint work on `main` under `[Unreleased]`, additive.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-16 | Darren Benson (operator) / Dani Okafor seat | Sprint-close review, written to LATEST.md |
| 2026-07-16 | Claude Fable 5 | Preserved into RV0009 ahead of the unified review rewriting LATEST.md |
