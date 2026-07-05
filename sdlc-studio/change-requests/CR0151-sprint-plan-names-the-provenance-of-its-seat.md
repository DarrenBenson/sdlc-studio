# CR-0151: sprint plan names the provenance of its seat scores (which units were scored, and when)

> **Status:** Complete
> **Priority:** Low
> **Type:** Improvement
> **Date:** 2026-07-04
> **Created-by:** sdlc-studio file

## Summary

wsjf-inputs.json is a silent cross-sprint side-channel: the amigo consult writes it, and any LATER plan re-reads it without comment. Sprint 3's plan consumed the file sprint 2's consult wrote; the unit ids did not overlap so nothing misfired, but a recurring id would silently inherit months-old value/risk/size scores. Same staleness disease the mutation report had (CR0146): evidence consumed without checking it is about the present. The plan should say which units carry seat inputs and how fresh they are, so a stale consult is visible at the STOP where the operator signs off.

## Acceptance Criteria

- [ ] sprint plan output (text and the persisted sprint-plan.json) records per unit whether seat inputs applied, and the wsjf-inputs file's write time; units in the batch WITHOUT seat inputs are named (priority-fallback disclosure)
- [ ] a wsjf-inputs file older than a configurable window (default 7 days) draws an advisory staleness warning at plan time - never a refusal
- [ ] unit tests pin scored/unscored/stale cases; CHANGELOG [Unreleased]

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-04 | audit | Raised |
| 2026-07-04 | operator | Review: SOLID, preventive (no actual misfire; latent staleness real). Quibble recorded: the 7-day window is somewhat arbitrary - seat judgement does not rot on a clock like a mutation report; harmless because advisory-only |
| 2026-07-05 | Claude (sprint 2026-07-D) | Delivered in sprint 2026-07-D (8c8350e): seat_provenance in build_plan + plan text; staleness advisory window sprint.wsjf_inputs_stale_days; age clamped at 0 (critic F9) |
