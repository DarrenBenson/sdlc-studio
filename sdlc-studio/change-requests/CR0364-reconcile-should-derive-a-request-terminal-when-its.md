# CR-0364: reconcile should derive a request terminal when its children are all resolved - G2 is a gate with no counterpart

> **Status:** Complete
> **Decomposed-into:** EP0087
> **Priority:** High
> **Type:** Improvement
> **Size:** M
> **Affects:** .claude/skills/sdlc-studio/scripts/reconcile.py, .claude/skills/sdlc-studio/scripts/tests/test_reconcile.py, .claude/skills/sdlc-studio/reference-reconcile.md
> **Date:** 2026-07-19
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1

## Summary

The two-backlog workflow states that a discovery item reaches its successful terminal by DERIVATION, never by assertion. refine and triage both print that promise to the operator at decompose time. transition enforces the guard half: `_request_terminal_gate` refuses a CR reaching Complete, an RFC Accepted or an Issue Resolved until every child is resolved. NOTHING PERFORMS THE DERIVATION. No script walks the requests whose children have since all resolved and closes them, and reconcile has no drift kind for the condition - its `DRIFT_KINDS` carries undecomposed (a request with NO children) but nothing for children-all-done-yet-parent-open. The result on this repo, measured: 34 of 59 open CRs are In Progress with every delivering epic already Done, and a five-agent evidence sweep confirmed 26 of them have every acceptance criterion satisfied. The discovery backlog over-reported remaining work by roughly 44 per cent, which silently corrupted sizing, velocity and launch-date estimates until someone checked artefact by artefact. Prior art shows the shape is already understood: `sprint._derive_parent_epics` solves precisely this one level down for epics, and its docstring records that an epic otherwise sat at Draft and had to be moved by hand. That fix was deliberately scoped to the parents of one run's units, so it never generalised upward to requests. This is not a dogfooding quirk. Any consuming project that sets `two_backlog.enforce` true - which the skill actively recommends - accumulates the same phantom backlog, and the more disciplined the project the worse it gets, because the gate is what keeps the request open.

## Impact

Every project using the two-backlog workflow. A backlog that over-reports by half makes planning, sizing and forecasting unreliable in a way nothing surfaces: the artefacts look healthy, reconcile reports zero drift, and the census is quietly wrong. It also punishes discipline - the G2 gate is what holds the request open, so a project that enforces the workflow accrues more phantom work than one that does not.

## Acceptance Criteria

- [ ] reconcile detect reports a request (CR/RFC/Issue) whose children are ALL resolved but whose own status is not terminal, as a named drift kind registered in `DRIFT_KINDS`
- [ ] reconcile apply transitions such a request to its successful terminal (Complete / Accepted / Resolved), through transition so every existing gate and cascade still runs
- [ ] a request with NO children is never derived - that is the existing undecomposed case and it stays distinct, since producing nothing is not delivering something
- [ ] a request with one or more unresolved children is never derived, and a child that was legitimately dropped (Won't Implement, Won't Fix, Rejected) counts as resolved, matching the G2 gate's own definition
- [ ] the derivation is a no-op on a project that does not enforce the two-backlog workflow, so an unenforced project keeps closing requests by assertion exactly as before
- [ ] running detect then apply on this repo derives the requests whose epics are already Done, and a second run reports zero further drift

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-19 | sdlc-studio | Raised |
