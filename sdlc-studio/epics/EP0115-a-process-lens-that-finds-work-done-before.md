# EP0115: A process lens that finds work done before the contract it depends on

> **Status:** Done
> **Derived Point Total:** 10
> **Parent:** CR0403
> **Created:** 2026-07-22
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Size:** L

## Summary

Decomposed from CR0403. Delivers the work CR0403 requested.

## Story Breakdown

- [x] [US0340: A process audit lens pack ships alongside test, with lenses drawn from failures this project actually produced](../stories/US0340-a-process-audit-lens-pack-ships-alongside-test.md)
- [x] [US0341: Each lens names its mechanically detectable signature, and where there is none it says so rather than implying a check that does not exist](../stories/US0341-each-lens-names-its-mechanically-detectable-signature-and.md)
- [x] [US0342: Every lens cites the incident it derives from, so a reader can weigh it against evidence rather than assertion](../stories/US0342-every-lens-cites-the-incident-it-derives-from.md)

## Acceptance Criteria (Epic Level)

- [ ] A `process` (or equivalently named) audit lens profile ships alongside `test`, with lenses drawn from failures this project actually produced rather than invented ones.
- [ ] Each lens names a mechanically detectable signature where one exists - a commit that repairs a review finding with no recorded plan; an artefact field whose value was never resolved against the tree; a hand-maintained count or enumeration beside the mechanism it describes.
- [ ] Where a signature is NOT mechanically detectable, the lens says so rather than implying a check that does not exist.
- [ ] Every lens cites the incident it derives from, so a reader can weigh it against evidence rather than assertion.

> Carried from the request. Author each story's own ACs against its
> slice while grooming - these are the epic's completion bar, not any
> single story's.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-22 | sdlc-studio | Created via `new` (deterministic) |
