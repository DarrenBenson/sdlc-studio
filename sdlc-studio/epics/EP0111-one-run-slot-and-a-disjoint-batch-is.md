# EP0111: One run slot, and a disjoint batch is refused rather than fused

> **Status:** Done
> **Derived Point Total:** 12
> **Parent:** CR0401
> **Created:** 2026-07-22
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Size:** L

## Summary

Decomposed from CR0401. Delivers the work CR0401 requested.

## Story Breakdown

- [x] [US0326: sprint plan --write refuses a disjoint batch against an open run, exiting non-zero with run-state.json byte-identical](../stories/US0326-sprint-plan-write-refuses-a-disjoint-batch-against.md)
- [x] [US0327: The refusal names the open run's id, outcome and batch size, and states both ways forward](../stories/US0327-the-refusal-names-the-open-run-s-id.md)
- [x] [US0328: A run whose only close artefact is a FAILED close attempt is open-and-protected, not absorbable](../stories/US0328-a-run-whose-only-close-artefact-is-a.md)
- [x] [US0329: help/sprint.md states the single run slot and what planning a second batch against an open run does](../stories/US0329-help-sprint-md-states-the-single-run-slot.md)

## Acceptance Criteria (Epic Level)

- [ ] Planning a batch with --write, against a repository whose open run holds a disjoint batch, refuses: it exits non-zero and run-state.json is byte-identical afterwards. Today it succeeds and the two batches are fused.
- [ ] The refusal names the open run's id, its outcome and its current batch size, and states both ways forward - close that run, or re-plan it deliberately - so the operator can act without reading the source.
- [ ] A genuine re-plan, where the incoming batch overlaps the open run's, still accumulates exactly as it does today, and needs no new flag to do so.
- [ ] A run whose only close artefact is a FAILED close attempt is treated as open-and-protected rather than absorbable. A recorded close attempt currently leaves a run fully absorbable, which is the case most likely to be hit.
- [ ] help/sprint.md states that there is a single run slot, and says what happens when a second batch is planned while a run is open.

> Carried from the request. Author each story's own ACs against its
> slice while grooming - these are the epic's completion bar, not any
> single story's.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-22 | sdlc-studio | Created via `new` (deterministic) |
