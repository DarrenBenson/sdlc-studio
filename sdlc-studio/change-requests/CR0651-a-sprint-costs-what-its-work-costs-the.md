# CR-0651: A sprint costs what its work costs: the meter reads true, each unit is built and reviewed in a small fresh context, and a regression is caught at the close

> **Status:** In Progress
> **Decomposed-into:** EP0292
> **Created:** 2026-10-22
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/lib/run_state.py, .claude/skills/sdlc-studio/scripts/critic.py, .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/reference-sprint.md
> **Priority:** High
> **Type:** Enhancement

## Summary

A sprint run with this skill costs several times what its work needs, and the meter hides it. Measured from this project's transcripts (priced: input 1, cache write 1.25, cache read 0.1, output 5), run one cost 74.5M (2.0M per point) and run two 78.2M (3.0M per point). The orchestrating main thread is 73-75% of that, and cache reads are 83-85% of its cost: the whole run is driven from one context averaging about 500k tokens, re-read on every turn (about 67k priced per turn, against about 13k for a reviewer in a fresh context). A unit review averages 1.9M at a median of 72 turns, most of them exploring the change; the review brief carries neither the diff nor the command that runs the unit's Verify lines, and the light tier is about 5% smaller than full. The meter shows about a third of the real figure: it counts a message once per content block (BG1111), excludes cache reads and excludes subagents, so a user reads the wrong total and the wrong cause. Goal reviews ran two to four rounds of three seats. Nothing notices a run that costs more per point than the last ones. Operator ruling D0389: this ships in 6.2.

## Impact

Users of the skill pay for the orchestrator's context, not the work. A user who reads the meter sees a third of the spend and cannot tell the orchestrator's context is the cause.

## Acceptance Criteria

_None yet: add them here, or on the stories `refine` decomposes this into._

## Recommendation

Refine into one epic of five stories, delivered in run three after EP0291 and BG1111 (D0389): E1 the meter includes subagents and prices cache reads; E2 a builder brief per unit and a delivery loop that builds each unit in a fresh agent; E3 the review brief carries the bounded diff and the Verify command, the light tier is lighter, and each tier states a tool-call budget; E4 the close flags a run over 1.5 times the trailing median cost per point as a known issue, with a per-unit breakdown, and the retro names the cause; E5 one goal-review round by default.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-22 | sdlc-studio | Created via `new` (deterministic) |
