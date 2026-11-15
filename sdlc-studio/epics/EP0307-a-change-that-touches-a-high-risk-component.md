# EP0307: A change that touches a high-risk component is classed from a declared map, flagged at plan and reviewed by a second independent seat whose yield is reported

> **Status:** Done
> **Derived Point Total:** 8
> **Parent:** CR0696
> **Created:** 2026-11-14
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Size:** M

## Summary

Decomposed from CR0696. Delivers the work CR0696 requested.

## Story Breakdown

- [x] [US1152: A declared component map gives each story a risk and compliance class at refine](../stories/US1152-a-declared-component-map-gives-each-story-a.md)
- [x] [US1153: sprint plan shows each unit's class and flags a unit that touches a higher class than its tag](../stories/US1153-sprint-plan-shows-each-unit-s-class-and.md)
- [x] [US1154: A high-class unit gets a second independent review seat, and the retro reports what that seat found](../stories/US1154-a-high-class-unit-gets-a-second-independent.md)

## Acceptance Criteria (Epic Level)

- [ ] A project declares its component map (paths to a class, such as payments, personal data or standard) in one committed file, and refine sets each unit's class from it
- [ ] `sprint plan` flags a unit whose Affects touch a component of a higher class than its tag, and the plan shows each unit's class for approval; no per-unit sign-off is added
- [ ] A high-class unit gets a second independent review seat, briefed with `critic.py brief`, and the retro reports what each second seat found that the first did not
- [ ] A project with no map classes every unit standard and the plan says so in one line; nothing refuses

> Carried from the request. Author each story's own ACs against its
> slice while grooming - these are the epic's completion bar, not any
> single story's.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-14 | sdlc-studio | Created via `new` (deterministic) |
