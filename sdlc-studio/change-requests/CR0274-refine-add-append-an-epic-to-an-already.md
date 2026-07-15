# CR-0274: refine --add: append an epic to an already-decomposed request, for incremental slices

> **Status:** Complete
> **Decomposed-into:** EP0036
> **Priority:** P1
> **Type:** Improvement
> **Size:** M
> **Affects:** .claude/skills/sdlc-studio/scripts/refine.py
> **Date:** 2026-07-15
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1

## Summary

refine apply refuses a request that already carries a Decomposed-into (refine a request once). But a large request (RFC0039, RFC0040) is delivered in SLICES - one epic per sprint - so its second and later epics cannot be wired with refine at all; they need hand-wiring, which is the friction refine exists to remove. Add a mode (refine add, or apply --add) that appends a NEW epic + stories to an already-decomposed request: it writes the epic's Parent, appends the epic id to the request's Decomposed-into (never clobbering the existing children), and rolls the new epic's own point total.

## Impact

BLOCKS the P1 release path: RFC0040's remaining work (the migration pass, docs, 5.0.0) is a second epic under RFC0040, and refine refuses it because EP0034 is already there. Same for RFC0039's Issue/triage slices. Discovered dogfooding the v5 spine (RETRO0031 action, now a first-class CR). Belongs in RFC0039's refine workstream. Care: --add must be ATOMIC like apply (validate all input up front, roll back on failure), must not create a duplicate epic if re-run, and must keep the Decomposed-into list append-only so earlier slices are never lost.

## Acceptance Criteria

- [ ] refine can append a second epic + stories to a request that already has a Decomposed-into, writing the new epic's Parent and APPENDING its id to the request's Decomposed-into (existing children preserved)
- [ ] the append path is atomic (all input validated up front, rollback on a mid-create failure) and idempotent-safe (does not duplicate or clobber existing children)
- [ ] after an add, reconcile shows no link-asymmetry and the request resolves to all its epics via `children_of`
- [ ] a test pins that a second refine --add onto an already-decomposed request wires the new epic without losing the first

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-15 | sdlc-studio | Raised |
