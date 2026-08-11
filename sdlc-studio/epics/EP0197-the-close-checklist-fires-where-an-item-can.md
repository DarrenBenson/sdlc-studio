# EP0197: The close checklist fires where an item can still be satisfied, and reads verdicts rather than counts

> **Status:** Done
> **Derived Point Total:** 24
> **Parent:** CR0513
> **Created:** 2026-08-01
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Size:** XL

## Summary

Decomposed from CR0513. Delivers the work CR0513 requested.

## Story Breakdown

- [x] [US0591: Every checklist item declares its enforcing command, and the close reports rather than gates on an expired window](../stories/US0591-every-checklist-item-declares-its-enforcing-command-and.md)
- [x] [US0592: The goal seat review is enforced by sprint plan --write, so skipping it is refused where it can still be run](../stories/US0592-the-goal-seat-review-is-enforced-by-sprint.md)
- [x] [US0593: A run whose only review verdicts are REJECT reports the closing-review item outstanding, never ran](../stories/US0593-a-run-whose-only-review-verdicts-are-reject.md)
- [x] [US0594: A unit whose ticked criteria the tree contradicts is reported outstanding at the close](../stories/US0594-a-unit-whose-ticked-criteria-the-tree-contradicts.md)
- [x] [US0595: A waiver records whether it was deliberate or its window had already expired, and the retro counts them apart](../stories/US0595-a-waiver-records-whether-it-was-deliberate-or.md)
- [x] [US0596: Coverage is computed once, and two rows disagreeing about it is itself an outstanding item](../stories/US0596-coverage-is-computed-once-and-two-rows-disagreeing.md)

## Acceptance Criteria (Epic Level)

- [ ] Every checklist item declares its enforcing command, and an item whose window closes before the close is enforced there - proven by a test in which skipping the goal review fails `sprint plan --write` rather than surfacing at the close
- [ ] A run whose only recorded review verdicts are REJECT reports the closing-review item as OUTSTANDING, not `[ran]` - the positive control being that an APPROVE covering every unit passes
- [ ] A verdict whose brief did not come from `critic.py brief` is detected and reported, proven by recording one hand-written verdict and one tool-briefed verdict and asserting they resolve differently
- [ ] A unit whose ticked criteria the tree contradicts is reported OUTSTANDING, proven against a unit whose story file is byte-identical to the base ref while its criteria are ticked
- [ ] A waiver records its kind, and a window-expired waiver is counted separately in the retro from a deliberate one
- [ ] Two checklist rows cannot report different answers to the same coverage question; a disagreement is itself an outstanding item
- [ ] Replayed against RUN-01KYX375, the checklist reports the three items this run passed or waived as outstanding, and the measured before/after is recorded rather than asserted

> Carried from the request. Author each story's own ACs against its
> slice while grooming - these are the epic's completion bar, not any
> single story's.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-01 | sdlc-studio | Created via `new` (deterministic) |
