# EP0225: A delegated review cannot begin against a tree the unit is not in

> **Status:** Draft
> **Derived Point Total:** 6
> **Parent:** CR0509
> **Created:** 2026-08-27
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Size:** M

## Summary

Decomposed from CR0509. Delivers the work CR0509 requested.

## Story Breakdown

- [ ] [US0722: `critic.py brief` REFUSES when the working tree does not contain the unit, naming base found and base needed](../stories/US0722-critic-py-brief-refuses-when-the-working-tree.md)
- [ ] [US0723: A verdict records the base commit the review was measured against](../stories/US0723-a-verdict-records-the-base-commit-the-review.md)
- [ ] [US0724: `reference-review.md` states the base contract, so it is in the doctrine and not only in the tool](../stories/US0724-reference-review-md-states-the-base-contract-so.md)

## Acceptance Criteria (Epic Level)

- [ ] critic.py brief REFUSES when the working tree does not contain the unit under review, naming the base it found and what it needed, so a reviewer cannot begin against a tree the unit does not exist in
- [ ] A returned verdict records the base commit the review was measured against, so a verdict against a stale tree is visible in the record rather than indistinguishable from a current one
- [ ] reference-review.md states the base contract for a delegated review, so the requirement is in the shipped doctrine and not only in the tool

> Carried from the request. Author each story's own ACs against its
> slice while grooming - these are the epic's completion bar, not any
> single story's.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-27 | sdlc-studio | Created via `new` (deterministic) |
