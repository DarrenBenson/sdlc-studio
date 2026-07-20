# CR-0350: record the sprint's token actuals automatically for an interactive run

> **Status:** Complete
> **Decomposed-into:** EP0091
> **Priority:** Medium
> **Type:** Improvement
> **Size:** S
> **Affects:** .claude/skills/sdlc-studio/scripts/retro.py, .claude/skills/sdlc-studio/scripts/sprint.py
> **Date:** 2026-07-19
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1

## Summary

This run closed with tokens reported as not-yet-captured, exactly as the previous four did. The retro template explains at length that the number is measurable and must not be written off as unknowable, and offers 'retro.py accuracy --tokens N' - but nothing supplies N, so every interactive sprint closes with the estimate half of estimate-versus-actual permanently empty. Five consecutive retros now carry the same gap, which is long enough to call it a missing mechanism rather than forgetfulness. This overlaps CR0278 and should probably absorb it.

## Impact

The forecast model cannot calibrate. Every run records a forecast and no actual, so the tokens-per-point rate stays the shipped seed for ever and the plan's own warning that a fit to a couple of sprints fits noise can never be acted on.

## Acceptance Criteria

- [ ] an interactive close captures the harness-tracked token total without the operator supplying it by hand, or states plainly at the close that it could not and why
- [ ] the velocity row records the actual, so estimate-versus-actual closes for interactive runs as it does for runner ones

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-19 | sdlc-studio | Raised |
