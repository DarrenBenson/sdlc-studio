# EP0113: A REJECT can be carried forward as filed findings, under a declared policy

> **Status:** Done
> **Derived Point Total:** 13
> **Parent:** CR0404
> **Created:** 2026-07-22
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Size:** L

## Summary

Decomposed from CR0404. Delivers the work CR0404 requested.

## Story Breakdown

- [x] [US0332: A project declares a review policy: block-on-REJECT, today's behaviour and the default, or carry-forward](../stories/US0332-a-project-declares-a-review-policy-block-on.md)
- [x] [US0333: Under carry-forward every finding is FILED or explicitly waived with a reason; narrative downgrade is refused, as it already is for a missing review leg](../stories/US0333-under-carry-forward-every-finding-is-filed-or.md)
- [x] [US0334: The close records which policy was in force and lists the findings carried, so a converged sprint is distinguishable from one that carried findings](../stories/US0334-the-close-records-which-policy-was-in-force.md)
- [x] [US0335: A carried-forward finding is linked to the units it was found against, so it cannot be lost when the sprint closes](../stories/US0335-a-carried-forward-finding-is-linked-to-the.md)

## Acceptance Criteria (Epic Level)

- [ ] A project can declare a review policy: block on REJECT (today's behaviour, and the default so nothing changes), or carry forward - the findings are FILED as artefacts and the sprint proceeds.
- [ ] Under carry-forward, every finding must be filed or explicitly waived with a reason, exactly as a missing review leg already is. Narrative downgrade is refused in both cases.
- [ ] The close records which policy was in force and lists the findings carried, so a reader can tell a sprint that converged from one that carried findings forward.
- [ ] A carried-forward finding is linked to the units it was found against, so it cannot be lost when the sprint closes.

> Carried from the request. Author each story's own ACs against its
> slice while grooming - these are the epic's completion bar, not any
> single story's.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-22 | sdlc-studio | Created via `new` (deterministic) |
