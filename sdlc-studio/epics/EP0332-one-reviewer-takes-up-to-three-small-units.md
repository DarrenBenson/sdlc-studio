# EP0332: One reviewer takes up to three small units of a wave, and a fresh round two reviewer is named

> **Status:** Draft
> **Derived Point Total:** 9
> **Parent:** CR0680
> **Created:** 2026-11-17
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Size:** L

## Summary

Decomposed from CR0680. Delivers the work CR0680 requested.

## Story Breakdown

- [ ] [US1217: Critic record accepts a round two verdict from a fresh reviewer and records it under its own name](../stories/US1217-critic-record-accepts-a-round-two-verdict-from.md)
- [ ] [US1218: Critic brief given several units prints the stable blocks once and each unit's scope, criteria and diff apart](../stories/US1218-critic-brief-given-several-units-prints-the-stable.md)
- [ ] [US1219: The review dispatch groups a wave's units of at most 3 points into reviewer batches of at most three](../stories/US1219-the-review-dispatch-groups-a-wave-s-units.md)

## Acceptance Criteria (Epic Level)

- [ ] The review dispatch groups the units of one landing or wave into reviewer batches of at most three units of at most 3 points each and emits one dispatch naming each unit's brief and verdict path, with independence from the author unchanged.
- [ ] `critic.py brief` given several --unit values prints the stable blocks (seat charter, practices, lessons, return contract) once and each unit's scope, criteria and diff apart.
- [ ] `critic.py record` accepts a round-2 verdict from a reviewer other than round 1's and records each under its own name, and the cost anatomy (US1124) attributes the round-2 transcript to it.
- [ ] Before and after: the next sprint reports per-unit review cost and finding yield for batched and single reviews against run six's 330k single and 266k batched round 1.

> Carried from the request. Author each story's own ACs against its
> slice while grooming - these are the epic's completion bar, not any
> single story's.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-17 | sdlc-studio | Created via `new` (deterministic) |
