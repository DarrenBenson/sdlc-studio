# EP0184: A seam between two units has an owner before the work starts

> **Status:** Draft
> **Derived Point Total:** 11
> **Parent:** CR0468
> **Created:** 2026-07-28
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Size:** L

## Summary

Decomposed from CR0468. Delivers the work CR0468 requested.

## Story Breakdown

- [ ] [US0538: Refine computes the seam map for a batch and reports a pair sharing a property with no criterion asserting it is preserved](../stories/US0538-refine-computes-the-seam-map-for-a-batch.md)
- [ ] [US0539: The seam map reaches the delivery lane brief and the review brief, so a lane is told which neighbouring property it must not regress](../stories/US0539-the-seam-map-reaches-the-delivery-lane-brief.md)
- [ ] [US0540: The close reports seam coverage beside the points, and a batch that shipped with unowned seams says so](../stories/US0540-the-close-reports-seam-coverage-beside-the-points.md)

## Acceptance Criteria (Epic Level)

- [ ] Refine computes and reports the seam map for a batch - pairs of units touching the same file, symbol or stated property - and a pair sharing a property with no criterion asserting that property is preserved is reported at plan time, proven by a test written red before the fix over a fixture reproducing the US0529 and US0530 pair
- [ ] The seam map reaches the delivery lane brief and the review brief, so a lane is told which neighbouring property it must not regress, proven by a test asserting the brief content rather than the map's existence
- [ ] The close reports seam coverage beside the points, and a batch that shipped with unowned seams reports them rather than omitting the line, proven by a test written red before the fix

> Carried from the request. Author each story's own ACs against its
> slice while grooming - these are the epic's completion bar, not any
> single story's.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-28 | sdlc-studio | Created via `new` (deterministic) |
