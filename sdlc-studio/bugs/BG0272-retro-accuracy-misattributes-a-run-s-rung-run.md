# BG0272: retro accuracy misattributes a run's rung: _run_rung reads the CURRENT run state, so re-running retro/sprint-report for an older retro after a new run opened reads the wrong goal rung

> **Status:** Open
> **Created:** 2026-07-23
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/retro.py
> **Severity:** Medium
> **Points:** 3

## Summary

{{symptom}}

## Steps to Reproduce

{{steps}}

## Proposed Fix

{{fix}}

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-23 | sdlc-studio | Created via `new` (deterministic) |

## Acceptance Criteria

- [ ] the retro reads the rung of the run it belongs to, not the current run state
- **Given** an older retro is re-run after a newer run has opened (which re-stamps the run-state goal)
- **Then** the retro reads the rung of the run it belongs to, not the current run state
- **Verify:** manual
