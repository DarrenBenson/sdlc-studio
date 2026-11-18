# EP0376: Review in this repository treats a change to a gate as high risk

> **Status:** Done
> **Derived Point Total:** 5
> **Parent:** CR0739
> **Created:** 2026-11-17
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Size:** M

## Summary

Decomposed from CR0739. Delivers the work CR0739 requested.

## Story Breakdown

- [x] [US1313: This repository's config declares the D0520 component map, and a test pins each gate script to high](../stories/US1313-this-repository-s-config-declares-the-d0520-component.md)
- [x] [US1314: Reconcile reports a story whose stamped risk class is below the class its Affects now get from the map, and apply raises it](../stories/US1314-reconcile-reports-a-story-whose-stamped-risk-class.md)

## Acceptance Criteria (Epic Level)

- [ ] `sdlc-studio/.config.yaml` declares the D0520 map and `lib/risk_class.py` loads it with no notes
- [ ] Open stories whose Affects touch a mapped path carry the class the map gives

> Carried from the request. Author each story's own ACs against its
> slice while grooming - these are the epic's completion bar, not any
> single story's.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-17 | sdlc-studio | Created via `new` (deterministic) |
