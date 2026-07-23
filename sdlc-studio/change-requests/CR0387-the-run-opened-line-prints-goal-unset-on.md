# CR-0387: The run-opened line prints goal=unset on the same command that just set the Sprint Goal

> **Status:** In Progress
> **Decomposed-into:** EP0143
> **Priority:** Low
> **Type:** Improvement
> **Size:** S
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py
> **Date:** 2026-07-21
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1

## Summary

Running `sprint plan --write --sprint-goal '<text>'` prints: 'opened run RUN-01KY321Q (goal=unset, appetite 240min/8units)'. The Sprint Goal WAS recorded - run-state.json carries it correctly - and the `goal` being reported as unset is the separate --goal ladder rung (triage / plan / design / done), which the command did not pass. Two different fields both called 'goal', reported in the line that confirms the write, one of them named exactly like the flag the operator just used. The reasonable reading is that the goal did not take, which invites a re-run of the plan against a run that is already open. Observed twice, on two consecutive sprints, by an operator who had passed --sprint-goal deliberately in both.

## Impact

Every operator and agent opening a run with a Sprint Goal, which the sprint workflow prompts for and does not invent. The confirmation line is the only feedback that the write happened, so it is the one place ambiguity is most expensive. The failure mode is a re-plan against an already-open run to 'fix' a goal that was never broken - and a re-plan is exactly the operation BG0236's baseline logic deliberately makes non-idempotent (it refuses to re-stamp), so the confusion costs more now than it did before that fix landed.

## Acceptance Criteria

- [ ] The line that confirms a run opened distinguishes the Sprint Goal from the --goal ladder rung by name, so neither can be read as the other
- [ ] When a Sprint Goal was supplied it is shown as set, not reported as unset under a different field's name
- [ ] When no Sprint Goal was supplied the line says so, since the workflow requires one and never invents it
- [ ] A test drives the plan both with and without --sprint-goal and asserts the confirmation text differs, so the two cases cannot render identically

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-21 | sdlc-studio | Raised |
