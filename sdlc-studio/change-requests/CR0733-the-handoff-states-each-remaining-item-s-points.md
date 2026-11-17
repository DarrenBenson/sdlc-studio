# CR-0733: The handoff states each remaining item's points and the seat it needs, and totals them

> **Status:** In Progress
> **Decomposed-into:** EP0370
> **Priority:** Low
> **Type:** Improvement
> **Size:** S
> **Affects:** .claude/skills/sdlc-studio/scripts/handoff.py, .claude/skills/sdlc-studio/help/sprint.md, tools/tests/test_handoff_effort.py, .claude/skills/sdlc-studio/scripts/tests/test_handoff.py
> **Evidence:** competitor review 2026-11-17: published accounts of a commercial autonomous-delivery platform (Blitzy), chiefly its CEO and CTO interview on The Cognitive Revolution (January 2026) and the Quesma audit of its SWE-Bench Pro run; compared against this skill by grep
> **Date:** 2026-11-17
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-17T21:37:56Z

## Summary

`handoff show` lists what a run left behind, each item with its pointer, a difficulty band and a copilot-tail or judgement tag. It does not say how much work remains or who should pick it up. A commercial platform's per-delivery guide lists remaining tasks with an effort figure and the skill each needs, which is what lets a lead staff the tail in one read. Each remaining item already carries Points and a risk class; print them, name the seat (engineering, product or qa) whose charter covers the item's stalled stage, and total the points by tag and by seat.

## Impact

The operator reading a partial run's handoff, who today must open each unit to learn how much is left.

## Acceptance Criteria

- [ ] Each remaining item in `handoff show` carries its Points, or the word unsized when it has none, in both the text and the JSON output
- [ ] Each remaining item names one seat, derived from the stage it stalled at by a rule the help page states
- [ ] The handoff ends with remaining points totalled by suitability tag and by seat, and the totals re-add from the rows

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-17 | sdlc-studio | Raised |
