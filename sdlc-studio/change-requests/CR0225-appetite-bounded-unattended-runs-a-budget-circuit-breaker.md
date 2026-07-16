# CR-0225: appetite-bounded unattended runs: a budget circuit-breaker for epic-level execution

> **Status:** Complete
> **Size:** M
> **Target:** v4.1
> **Priority:** Medium
> **Type:** Feature
> **Date:** 2026-07-10
> **Created-by:** sdlc-studio file
> **Depends on:** CR0223

## Summary

v4.1 candidate, from the vendor white-paper comparison (their 'code generated overnight at the
speed of compute') fused with the Shape Up appetite pattern (a hard timebox with a circuit
breaker). sdlc-studio's agentic mode has per-unit `loop_guard` quarantine but no RUN-level
budget: an unattended epic run has no declared appetite, so it either runs to completion or to
failure. Add a declared appetite, a breaker that stops the run cleanly, and - paired with
CR0223 - an honest close: what the appetite bought, what remains. The appetite is never
extended autonomously (Shape Up's rule: appetite is fixed, scope flexes).

**Rescoped 2026-07-13** (see Revision History). Two things in the original ACs could not be
built honestly:

- **Token budget.** No script in this repo can observe token spend - `telemetry.py` says so
  in its own docstring: tokens are recorded only when the caller passes them, because a script
  cannot read them reliably. A token breaker would therefore depend on the orchestrating model
  self-reporting the very budget meant to constrain it. That is a suggestion, not a circuit
  breaker, and it contradicts the guardrail doctrine that the model cannot skip a deterministic
  check. Tokens become an **advisory forecast** (summed from the plan's existing per-unit
  estimate), clearly labelled as an estimate, never a gate.
- **Mid-unit resumability.** There is no checkpoint concept: `resume.py` derives a resume point
  from story Status alone, so a unit interrupted mid-implementation (files edited, tests red)
  has nothing to roll back to. The breaker therefore fires at **unit boundaries**, which
  collapses the cost and is the only honest option.

## Acceptance Criteria

- [ ] An agentic run accepts a declared appetite as wall-clock and/or unit count (`--appetite-minutes`, `--appetite-units`); both are deterministic and harness-independent
- [ ] The breaker is evaluated at unit boundaries and stops the run cleanly when the appetite is spent: no unit is ever abandoned mid-implementation
- [ ] Budget-exhausted is distinguishable from quarantine - its own exit code, and units are left in their true status rather than marked Blocked
- [ ] The run close reports appetite declared vs spent vs delivered, and generates the CR0223 handoff guide naming what remains
- [ ] The appetite is never auto-extended; extending it is an explicit operator action on a new run
- [ ] A token forecast from the plan's per-unit estimate is reported at plan time and at close, labelled an estimate and never used as a gate
- [ ] Mutation-checked: removing the boundary check turns a test red

## Impact

An unattended run today has exactly two outcomes: it finishes, or it fails. There is no way to
say "spend this much and no more", which is the precondition for trusting a run to go
unattended at all.

**Effort:** M

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-10 | audit | Raised |
| 2026-07-13 | Darren | Rescoped after implementation scoping: the token breaker is architecturally blocked (a script cannot observe token spend, so the budget would be self-reported by the actor it constrains) and "mid-unit resumable" has no checkpoint concept behind it. Appetite is now wall-clock + unit-count, fired at unit boundaries; tokens become an advisory forecast. `Depends on: CR0223` recorded - the run-state object and the handoff artefact are its foundation. |
