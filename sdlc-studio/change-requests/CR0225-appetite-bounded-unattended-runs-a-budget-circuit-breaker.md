# CR-0225: appetite-bounded unattended runs: a budget circuit-breaker for epic-level execution

> **Status:** Deferred
> **Target:** v4.1 (deliberately deferred past the GA tag; operator-directed 2026-07-10)
> **Priority:** Medium
> **Type:** Feature
> **Date:** 2026-07-10
> **Created-by:** sdlc-studio file

## Summary

v4.1 candidate, from the same vendor white-paper comparison (their 'code generated overnight at the speed of compute') fused with the Shape Up appetite pattern the frameworks research surfaced (operationalised as a hard timebox/budget with a circuit breaker). sdlc-studio's agentic mode has per-unit `loop_guard` quarantine but no RUN-level budget: an unattended epic run has no declared appetite, so it either runs to completion or to failure. Add a declared appetite to the sprint/epic run (token and/or wall-clock budget), a circuit breaker that stops the run cleanly at the boundary, and - paired with the handoff-guide CR - an honest close: what the appetite bought, what remains. Never extend the appetite autonomously (Shape Up's rule: appetite is fixed, scope flexes).

## Acceptance Criteria

- [ ] sprint/epic agentic runs accept a declared appetite (tokens and/or wall-clock); the breaker stops the run cleanly at the boundary, mid-unit work rolled to a resumable state
- [ ] The run close reports appetite spent vs delivered and generates the handoff guide; the appetite is never auto-extended

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-10 | audit | Raised |
