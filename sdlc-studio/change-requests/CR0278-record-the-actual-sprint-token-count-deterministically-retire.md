# CR-0278: Record the actual sprint token count deterministically; retire the interactive-equals-UNMEASURED doctrine

> **Status:** Complete
> **Decomposed-into:** EP0045
> **Priority:** Medium
> **Type:** Improvement
> **Size:** M
> **Affects:** .claude/skills/sdlc-studio/scripts/retro.py, .claude/skills/sdlc-studio/reference-retro.md
> **Date:** 2026-07-15
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1

## Summary

The retro accuracy block, VELOCITY.md and reference-retro treat an interactive sprint's token spend as UNMEASURED, on the premise that a script cannot observe token spend. That is wrong: the harness tracks the token count deterministically (a Workflow run reports it - the homelab audit reported ~6.9M tokens; an interactive run's total is on the session counter). Declaring it UNMEASURED conflates 'the skill's runner-only telemetry did not capture it' with 'unmeasurable', and blocks the estimate-vs-actual loop for exactly the interactive sprints being run. Capture the actual token count for an interactive sprint too (operator-supplied at retro time, or a harness/run-state hook), so tokens-per-point closes for every sprint.

## Impact

The velocity/estimator loop (CR0273 lineage) never closes for interactive sprints because the actual is declared unknowable. Operators reading RETRO0029-0037 see 'UNMEASURED' where a real number exists. Fix: retro.py accepts/records the actual token count (a --tokens flag at minimum; ideally read from the run-state the harness could stamp), the accuracy block computes tokens-per-point from it, and reference-retro/the template drop the 'interactive = UNMEASURED' language for 'not-yet-captured'. Keep the descriptive-never-a-target guard (CR0273).

## Acceptance Criteria

- [ ] retro.py records a real actual token count for an interactive sprint (e.g. retro.py accuracy --tokens N) and computes tokens-per-point from it
- [ ] reference-retro.md and the retro template stop calling an interactive sprint UNMEASURED and say not-yet-captured, with how to supply the count
- [ ] the descriptive-never-a-target and fixed-ceremony guards from CR0273 are preserved

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-15 | sdlc-studio | Raised |
