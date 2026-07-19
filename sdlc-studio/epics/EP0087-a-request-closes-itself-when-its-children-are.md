# EP0087: A request closes itself when its children are done: reconcile derives the terminal that G2 only ever guarded

> **Status:** Draft
> **Derived Point Total:** 8
> **Parent:** CR0364
> **Created:** 2026-07-19
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Size:** M

## Summary

Decomposed from CR0364. Delivers the work CR0364 requested.

## Story Breakdown

- [ ] [US0269: reconcile detect reports a derivable request as a registered drift kind, using the SAME predicate the G2 gate enforces](../stories/US0269-reconcile-detect-reports-a-derivable-request-as-a.md)
- [ ] [US0270: reconcile apply derives the request terminal through transition, so every gate and cascade still runs](../stories/US0270-reconcile-apply-derives-the-request-terminal-through-transition.md)
- [ ] [US0271: The derivation refuses what G2 refuses: no childless request, no unresolved child, and a no-op where the two-backlog workflow is unenforced](../stories/US0271-the-derivation-refuses-what-g2-refuses-no-childless.md)

## Acceptance Criteria (Epic Level)

- [ ] reconcile detect reports a request (CR/RFC/Issue) whose children are ALL resolved but whose own status is not terminal, as a named drift kind registered in `DRIFT_KINDS`
- [ ] reconcile apply transitions such a request to its successful terminal (Complete / Accepted / Resolved), through transition so every existing gate and cascade still runs
- [ ] a request with NO children is never derived - that is the existing undecomposed case and it stays distinct, since producing nothing is not delivering something
- [ ] a request with one or more unresolved children is never derived, and a child that was legitimately dropped (Won't Implement, Won't Fix, Rejected) counts as resolved, matching the G2 gate's own definition
- [ ] the derivation is a no-op on a project that does not enforce the two-backlog workflow, so an unenforced project keeps closing requests by assertion exactly as before
- [ ] running detect then apply on this repo derives the requests whose epics are already Done, and a second run reports zero further drift

> Carried from the request. Author each story's own ACs against its
> slice while grooming - these are the epic's completion bar, not any
> single story's.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-19 | sdlc-studio | Created via `new` (deterministic) |
