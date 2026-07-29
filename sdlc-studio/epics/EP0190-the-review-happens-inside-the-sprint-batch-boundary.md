# EP0190: The review happens inside the sprint: batch-boundary adversarial passes, so a finding is delivery work not close overhead

> **Status:** Draft
> **Derived Point Total:** 16
> **Parent:** CR0500
> **Created:** 2026-07-29
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Size:** L

## Summary

Decomposed from CR0500. Delivers the work CR0500 requested.

## Story Breakdown

- [ ] [US0560: A delivery batch reaching the commit threshold has a defined review point, and the adversarial pass takes that batch's units as its surface](../stories/US0560-a-delivery-batch-reaching-the-commit-threshold-has.md)
- [ ] [US0561: A batch-review finding is filed as a delivery unit against the batch that caused it, so its cost is priced where the work was](../stories/US0561-a-batch-review-finding-is-filed-as-a.md)
- [ ] [US0562: sprint close REFUSES a batch containing units no independent review has covered, and names them](../stories/US0562-sprint-close-refuses-a-batch-containing-units-no.md)
- [ ] [US0563: The shipped lifecycle states the batch-boundary cadence: doctrine, definition-of-done and help, so a consuming project inherits the placement](../stories/US0563-the-shipped-lifecycle-states-the-batch-boundary-cadence.md)

## Acceptance Criteria (Epic Level)

- [ ] A delivery batch reaching the project's commit threshold has a defined review point, and the review's surface is that batch rather than the whole sprint.
- [ ] A finding from a batch review is filed as a delivery unit against that batch, so its cost is priced where the work was rather than as close overhead.
- [ ] `sprint close` REFUSES a batch containing units no independent review has covered, and names them - the close asserts coverage rather than performing the review.
- [ ] A repair written in response to a finding is itself covered by a later batch review, never shipped self-reviewed.
- [ ] The run record carries close elapsed against delivery elapsed, so a close costing more than its sprint is visible rather than felt.
- [ ] The shipped definition-of-done and lifecycle documentation place the review at the batch boundary, so a consuming project inherits the corrected cadence rather than this one.

> Carried from the request. Author each story's own ACs against its
> slice while grooming - these are the epic's completion bar, not any
> single story's.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-29 | sdlc-studio | Created via `new` (deterministic) |
