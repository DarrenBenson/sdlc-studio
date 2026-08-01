# CR-0518: a sprint run has a tool runbook it is made to read before it plans

> **Status:** In Progress
> **Decomposed-into:** EP0202
> **Created:** 2026-08-01
> **Created-by:** sdlc-studio new
> **Provenance:** human
> **Raised-by:** Claude Opus 5; human; v1
> **Affects:** .claude/skills/sdlc-studio/reference-sprint-toolchain.md, .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/help/sprint.md
> **Priority:** High
> **Type:** Improvement
> **Size:** M

## Summary

reference-scripts.md is a catalogue of 40+ scripts ordered by script, and it answers 'what does X do'. Nobody planning a sprint has that question. The question at plan time is 'what is the next step and which command performs it', and no document answers it in that order. So the agent supplies the ordering from memory, and memory is where the hand-rolling comes from: a hand-written review prompt where critic.py brief exists, a hand-scripted backlog census where sprint breakdown exists, hand-rolled mutation harnesses where mutation.py run exists. Each was a step whose tool the agent did not recall AT THE MOMENT THE STEP AROSE.

Ship a runbook ordered by SPRINT STEP, not by script - plan, groom, batch, deliver a unit, review a unit, close - each step naming the one command that performs it, its fields-file path, and the hand-rolled shape it replaces. Then make sprint plan and sprint run PRINT it, so it is read at the moment it is needed rather than depending on the agent having read it earlier.

## Impact

The hand-rolling this repo keeps catching is not defiance, it is recall failure at a step boundary, and a catalogue ordered by script cannot fix a failure of step-to-command lookup. CR0515 detects hand-rolling AFTER the diff exists; this prevents it by putting the right command in front of the agent BEFORE the step. LL0027 says a rule that matters is gated in the command people actually run - printing the runbook from sprint plan is that gate's weakest useful form, and an acknowledgement gate is the strong one.

## Acceptance Criteria

- [ ] A runbook exists ordered by sprint STEP, not by script, covering plan, groom, batch,
      deliver a unit, review a unit and close - each step naming the one command that
      performs it and the fields-file path where prose is involved.
- [ ] Each step names the hand-rolled shape it replaces, so the entry is recognisable from
      the wrong instinct rather than only from the right one.
- [ ] `sprint plan` and `sprint run` print the runbook, so it reaches the agent at the step
      boundary rather than depending on it having been read earlier.
- [ ] A guard fails when a step in the runbook names a command that no longer exists, so the
      document cannot rot into advice for a tool that was renamed.
- [ ] The runbook is derived from the shipped command surface where it can be, not restated
      from memory - a hand-maintained list of commands is the same recall failure one level up.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-01 | Claude Opus 5 | Created via `new` (deterministic) |
