# CR-0378: a sprint must not stop while any unblocked unit remains: deferring one unit's decision may never park the batch

> **Status:** In Progress
> **Decomposed-into:** EP0099
> **Priority:** High
> **Type:** Improvement
> **Size:** M
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py,.claude/skills/sdlc-studio/reference-sprint.md,.claude/skills/sdlc-studio/scripts/lib/run_state.py
> **Date:** 2026-07-20
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1

## Summary

Observed in RUN-01KY03GS. One unit (BG0222) needed an operator decision, and the whole 13-unit sprint stopped waiting for it - while US0263, US0264, US0265 and BG0223 were entirely unblocked by that decision and could have been built meanwhile. The mechanism to prevent this ALREADY EXISTS: CR0369 shipped sprint decision defer, whose entire purpose is to set an undecidable unit aside while the batch continues, and decision list to ask everything accumulated together at one stop. Nothing obliges its use, nothing prompts it, and nothing prices the stop, so the available-but-optional path was not taken and the expensive one was. The rule wanted is that the loop continues while ANY unit remains that the pending question does not block, and stops only when nothing can proceed without an answer - an unresolvable situation, not merely an undecided one.

## Impact

A stop is expensive and its cost is invisible today, so nothing pushes back on taking one. It pollutes the elapsed wall-clock that is the denominator of the pts/elapsed-hour series BG0218 and US0279 have just made trustworthy: an idle gap makes that number a lie while it still reads as a measurement, which is the exact class of false-but-plausible number this project keeps paying to remove. It breaks the continuity the close review assumes, since the round-counting and repair-regression machinery reads a run as one continuous thing. And the failure mode is silent - a parked sprint looks like a careful one, so nobody reviews the decision to park it. Making the loop refuse to stop while unblocked work remains converts a judgement call into a property of the loop, the same move the two-role gate and the Done gate already make.

## Acceptance Criteria

- [ ] the sprint loop refuses to stop while any unit in the batch is unblocked by the pending question, and names the units it is continuing with
- [ ] deferring a unit decision never parks the batch: the remaining units continue and the question joins the accumulated queue asked together at the stop
- [ ] a stop records why it stopped and which units were blocked by it, so a parked run can be told from a finished one
- [ ] the elapsed wall-clock a run reports marks any idle gap, so pts/elapsed-hour is never computed over a period the run spent waiting rather than working
- [ ] an agent-initiated stop with unblocked work remaining is refused, and the refusal names defer as the path

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-20 | sdlc-studio | Raised |
