# CR-0194: Plan-stage adversarial review: independent AC-vs-spec check with a deterministic trigger

> **Status:** Proposed
> **Created:** 2026-07-08
> **Created-by:** sdlc-studio new
> **Priority:** High
> **Type:** process

## Summary

Close the "bad plan propagates" gap measured in the N=5 benchmark (D0014,
`docs/benchmarks/2026-07-08-n5-run.md`): in 2/5 mandated-planning runs the planner
mis-pinned a spec rule in the story's ACs, and the delivery critic - whose oracle IS the
story's ACs - approved the faithful implementation of the wrong plan. In one of the two
runs the worker then edited the workspace spec to match, falsifying the source of truth.
No step in the current pipeline independently checks the planner's ACs against the source
spec before implementation begins.

Add a plan-stage adversarial review: before a story with spec-derived ACs reaches
implementation, an independent reviewer (not the plan's author - the existing mechanical
author-is-not-reviewer gate extends to this seat) re-derives the constraining requirements
from the source spec and challenges each AC against them. Disagreement blocks the
implement step until resolved; the verdict is recorded alongside the critic's.

**The trigger must be deterministic, not judgement-scaled.** The same benchmark's
headline finding is that judgement-scaled hygiene is skipped under effort pressure 10/10
times; a plan review the model may decline is the same failure at one remove. Trigger on
checkable signals - the story's Affects (or its ACs) cite a spec/requirements document, or
`affects_files` at or above a threshold, or the routed difficulty band at or above medium -
so the gate fires by rule, with an operator override recorded to the ledger, never a
silent skip.

Scope guard: this adds a pass to plan-heavy units only. The routed pipeline already costs
~3.1x baseline per single ticket; the deterministic trigger keeps trivial and
non-spec-linked units at their current cost.

**Design constraint:** TRD ADR-006 applies - the fire/skip trigger is deterministic; model judgement acts only inside a fired step.

## Open decisions (resolve at design)

- Seat: extend the existing critic's charter with a plan-time invocation, or a distinct
  plan-reviewer seat (Three Amigos tester archetype is the natural fit).
- Trigger thresholds: which of the three signals, and their values, live in config.
- Whether the reviewer re-derives ACs blind (stronger, costlier) or challenges the
  written ACs directly (cheaper, anchoring risk).

## Acceptance Criteria

- [ ] A story whose ACs cite a spec document cannot enter implement without a recorded
      plan-review verdict from a reviewer distinct from the plan's author
- [ ] The trigger is evaluated deterministically from artifact fields and config, with no
      model judgement in the fire/skip decision; a skip is only possible via a recorded
      operator override
- [ ] The plan reviewer's charter explicitly includes re-checking each spec-derived AC
      against the cited source section, and flagging ACs that contradict or invert it
- [ ] Reference docs (sprint/story/critic) describe the gate; templates carry the verdict
      slot; telemetry records plan-review outcomes so the gate's value is measurable
- [ ] Benchmark note: a future arm or fixture rerun can measure whether the gate catches
      the seeded R5-inversion failure mode

## Evidence

- N=5 run: notify-digest arm R escapes n2/n3, both traced to planner AC inversion of SPEC
  R5 with critic APPROVE (D0014); worker spec falsification in n2.
- All 10 arm-R critic verdicts were APPROVE - the critic cannot catch a wrong oracle it
  inherits.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-08 | sdlc | Created via `new` (deterministic) |
| 2026-07-08 | claude | Filed from N=5 benchmark finding (D0014) |
