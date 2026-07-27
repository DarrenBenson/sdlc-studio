# CR-0435: A finding class that survives two audits becomes a deterministic detector

> **Status:** In Progress
> **Decomposed-into:** EP0169
> **Priority:** High
> **Type:** Improvement
> **Size:** M
> **Affects:** .claude/skills/sdlc-studio/reference-audit.md, .claude/skills/sdlc-studio/templates/audit-profiles/process.md, .claude/skills/sdlc-studio/scripts/gate.py
> **Date:** 2026-07-27
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Fable 5; agent; skill v5.0.0

## Summary

Adversarial audits keep re-deriving known weakness classes with model tokens: the 2026-07-27 project run cost 14.3M tokens and roughly a third of its survivors (version/count/timing drift, enumerated-list exemptions, dead Verify selectors) are mechanically checkable. The process profile already requires each lens to name its signature detector or declare none; this CR generalises that discipline into a conversion loop, so every recurring judgement becomes a free script and audit spend concentrates on what genuinely needs a model.

## Impact

Who: every consuming project that runs audit, and this repo's own dogfooding. What breaks without it: audit cost grows with the artifact graph while re-finding classes already paid for, the pre-flight cost gate keeps estimating runs that need not happen at that size, and the time/effort/cost value proposition erodes precisely where the skill claims to save it.

## Acceptance Criteria

- [ ] Audit close-out compares the run's survivors against prior runs' filed findings; a class filed in two separate runs is flagged detector-owed in the run report, with the mechanical check it implies named.
- [ ] The signature convention (each lens names its mechanical detector or states manual and why) is extended from the process profile to all six shipped lens packs.
- [ ] A detector-owed class gets a sized delivery unit to implement the check in gate/validate/reconcile, and once shipped the lens pack cites the detector so finders are told what the script now catches and skip it.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-27 | Claude Fable 5 | Raised |
