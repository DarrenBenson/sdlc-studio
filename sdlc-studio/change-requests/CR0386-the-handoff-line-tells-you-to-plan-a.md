# CR-0386: The handoff line tells you to plan a worklist that has zero items in it

> **Status:** In Progress
> **Decomposed-into:** EP0142
> **Priority:** Low
> **Type:** Improvement
> **Size:** S
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py
> **Date:** 2026-07-21
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1

## Summary

When the previous run closed with nothing outstanding, `sprint plan` still prints: 'handoff: the last run (goal-reached) left HO-0018 with 0 remaining item(s) - plan them with --worklist sdlc-studio/.local/handoff-worklist.txt'. The instruction cannot be followed usefully: the worklist file contains two comment lines and no ids. A clean handoff is GOOD NEWS and reads here as an outstanding action, so the one line that should say 'nothing carried over' instead adds a task. Minor on its own, but it appears at the top of every plan, and a prompt that is routinely wrong is how operators learn to skim the block that also carries the capacity warnings and the shared-file clusters.

## Impact

Every operator and agent running `sprint plan` after a clean close - which is the good case and should be the common one. The cost is attention rather than correctness: the handoff line is the first thing printed, so a false action item sits above the capacity, drift and shared-file-cluster warnings that genuinely need reading.

## Acceptance Criteria

- [ ] With 0 remaining items the line states that nothing carried over and offers no --worklist command
- [ ] With 1 or more remaining items the existing line is unchanged, naming the count and the worklist path
- [ ] The boundary is pinned two-sided by tests, so a future change cannot make the zero case reappear or suppress the non-zero one

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-21 | sdlc-studio | Raised |
