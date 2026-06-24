# CR-0107: sprint plan should emit dependency waves, not just a flat order

> **Status:** Complete
> **Priority:** Medium
> **Type:** Improvement
> **Date:** 2026-06-24
> **Created-by:** sdlc-studio file

## Summary

sprint plan returns a flat dependency-ordered list; the parallelisable wave structure (L1/L2/L3...) is only computed by the model at --agentic implement time. Two field transcripts show the agent hand-deriving the waves and recording the rich plan (goal + waves + DoD) in its own external plan.md because the skill's plan --write artifact is too thin to hold them. Emit the dependency levels deterministically in the plan output + the --write artifact.

## Acceptance Criteria

- [x] build_plan returns waves (dependency levels) for priority/wsjf order: wave 1 = no-dep units, wave n+1 = units whose in-batch deps are all in earlier waves; units in a wave are independent
- [x] sprint plan text output prints the waves (parallel marked); plan --write persists them; manual order has no waves
- [x] within a wave, units keep the same rank order as the flat plan (WSJF/priority); reuses the existing dep graph; unit test covers multi-level + parallel waves
- [x] documented in reference-sprint.md; CHANGELOG entry

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-06-24 | audit | Raised |
