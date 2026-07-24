# EP0160: The breakdown gate becomes goal-aware (CR0418 D0062)

> **Status:** Draft
> **Derived Point Total:** 6
> **Parent:** CR0418
> **Created:** 2026-07-24
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py

## Summary

{{what this epic groups}}

## Story Breakdown

- [ ] [US0430: the breakdown gate refuses an ungroomed batch at --goal done and accepts it at --goal design](../stories/US0430-the-breakdown-gate-refuses-an-ungroomed-batch-at.md)
- [ ] [US0431: a design rung's close reports how many units it groomed, so an accepted-but-ungroomed batch cannot close silently](../stories/US0431-a-design-rung-s-close-reports-how-many.md)

## Acceptance Criteria (Epic Level)

- [ ] The breakdown gate distinguishes the rung it is gating: an ungroomed batch is refused at `--goal done` and accepted at `--goal design`
- [ ] A design rung's close reports the grooming it produced, so an accepted-but-ungroomed batch cannot close silently
- [ ] The decision between A, B and C is recorded in the decisions ledger before the change lands

> Carried from the request. Author each story's own ACs against its
> slice while grooming - these are the epic's completion bar, not any
> single story's.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-24 | sdlc-studio | Created via `new` (deterministic) |
