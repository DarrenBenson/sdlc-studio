# CR-0436: Epic index Stories and Deps columns are dead for 156 of 165 epics and unchecked by reconcile

> **Status:** Proposed
> **Priority:** Low
> **Type:** Improvement
> **Size:** S
> **Affects:** sdlc-studio/epics/_index.md
> **Date:** 2026-07-27
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Fable 5 (adversarial audit wf_804ef18d carry-over, run wf_d141ccb5); agent; skill v5.0.0

## Summary

The index's only forward epic-to-story and epic-dependency traceability surface exists in name only: 9 of 165 rows populate Stories/Deps while every epic minted since shows --, including multi-story epics such as EP0163 (6 stories per the story index), and reconcile detect never flags the columns, so navigation requires opening each epic file or inverting the story index.

## Impact

The index's only forward epic-to-story and epic-dependency traceability surface exists in name only: 9 of 165 rows populate Stories/Deps while every epic minted since shows --, including multi-story epics such as EP0163 (6 stories per the story index), and reconcile detect never flags the columns, so navigation requires opening each epic file or inverting the story index.

## Acceptance Criteria

- [ ] Decide once: either teach reconcile (and artifact.py epic wiring) to derive and maintain Stories/Deps from story-index parent links and epic Dependencies sections with a drift check, or drop the two columns from the template and all four indexes so the surface stops asserting data it does not hold.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-27 | Claude Fable 5 (adversarial audit wf_804ef18d carry-over, run wf_d141ccb5) | Raised |
