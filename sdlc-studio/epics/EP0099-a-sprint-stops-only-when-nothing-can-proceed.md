# EP0099: A sprint stops only when nothing can proceed

> **Status:** Done
> **Derived Point Total:** 7
> **Parent:** CR0378
> **Created:** 2026-07-22
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Size:** M

## Summary

Decomposed from CR0378. Delivers the work CR0378 requested.

## Story Breakdown

- [x] [US0299: The loop continues while any unit the pending question does not block remains](../stories/US0299-the-loop-continues-while-any-unit-the-pending.md)
- [x] [US0300: A stop names what could have proceeded, so the cost of stopping is visible](../stories/US0300-a-stop-names-what-could-have-proceeded-so.md)

## Acceptance Criteria (Epic Level)

- [ ] the sprint loop refuses to stop while any unit in the batch is unblocked by the pending question, and names the units it is continuing with
- [ ] deferring a unit decision never parks the batch: the remaining units continue and the question joins the accumulated queue asked together at the stop
- [ ] a stop records why it stopped and which units were blocked by it, so a parked run can be told from a finished one
- [ ] the elapsed wall-clock a run reports marks any idle gap, so pts/elapsed-hour is never computed over a period the run spent waiting rather than working
- [ ] an agent-initiated stop with unblocked work remaining is refused, and the refusal names defer as the path

> Carried from the request. Author each story's own ACs against its
> slice while grooming - these are the epic's completion bar, not any
> single story's.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-22 | sdlc-studio | Created via `new` (deterministic) |
