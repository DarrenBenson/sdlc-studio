# CR-0721: Reconcile Draft US1034 and US1035 with the second seat that 6.4 delivered from the risk class under CR0696

> **Status:** In Progress
> **Decomposed-into:** EP0359
> **Priority:** Medium
> **Type:** Improvement
> **Size:** S
> **Affects:** sdlc-studio/stories/US1034-critic-py-seats-adds-a-second-different-seat.md, sdlc-studio/stories/US1035-the-sprint-report-names-a-high-risk-unit.md, sdlc-studio/epics/EP0284-review-seats-chosen-by-what-a-change-touches.md, sdlc-studio/change-requests/CR0622-a-second-different-seat-on-high-risk-units.md, sdlc-studio/decisions.md
> **Evidence:** audit AUDIT-2026-11-17, project profile, stories lens, survived 3 of 3 refute votes; observed at sdlc-studio/stories/US1034-critic-py-seats-adds-a-second-different-seat.md US1034 AC1-AC3 and Notes; US1035 AC1-AC3; EP0284 (Draft); CR0622 (In Progress), against US1152-US1154 and D0459/D0460
> **Date:** 2026-11-17
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-17T16:27:15Z

## Summary

Two definitions of a high-risk unit and its second review seat now sit in the backlog. Draft stories US1034 and US1035, under CR0622 and EP0284, specify a `critic.py seats` verb and the config keys `review.second_seat.points` and `review.second_seat.paths`, none of which exist at HEAD. Release 6.4 delivered the same capability differently in US1152 to US1154 under CR0696: a `risk.components` map, a `Risk-class` field and `sprint plan` naming the seat. Neither side references the other, and no decision rules which trigger wins. Built as written, the Draft stories would add a second config surface and a second, conflicting derivation of the same seat. US1034 also still carries its open triage items of 2026-10-21: no criterion for the AGENTS.md change, and conditionals left in its Notes.

## Impact

Whoever grooms EP0284 for 6.5 cannot bring US1034 or US1035 to Ready, because their criteria name a verb and config keys the delivered design replaced. An agent that builds them as written adds a duplicate, conflicting seat rule. US1035 is also the only planned unit that would make the sprint report name a high-risk unit reviewed by one seat, so that gap stays hidden behind a stale story.

## Acceptance Criteria

- [ ] A decision row in sdlc-studio/decisions.md states which trigger defines a high-risk unit (the Risk-class derived from risk.components, the points and paths thresholds, or a named combination) and cites CR0622 and CR0696
- [ ] US1034 is either closed as Superseded naming US1152 to US1154, or rewritten so that no criterion names critic.py seats or a `review.second_seat` key unless the decision keeps them, with its 2026-10-21 triage items resolved
- [ ] US1035 has criteria written against the delivered Risk-class and the seat that sprint plan names, so the sprint report row for a high-class unit reviewed by one seat has a Verify line that can run at HEAD
- [ ] CR0622 and EP0284 each name CR0696 and the delivered stories, so a reader of either side finds the other

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-17 | sdlc-studio | Raised |
