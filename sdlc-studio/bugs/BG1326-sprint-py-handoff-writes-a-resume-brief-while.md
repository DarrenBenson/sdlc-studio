# BG1326: `sprint.py handoff` writes a resume brief while a lane is still in flight, so the wave boundary reference-sprint.md defines is stated but not enforced, and four files still say no command writes a handoff

> **Status:** Open
> **Severity:** Low
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint_handoff.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py
> **Evidence:** US1142-verdict-r1 (RUN-01M7061X)
> **Created:** 2026-11-09
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5; human; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-09T19:03:27Z

## Summary

From US1142's QA review (qa-seat-US1142-r1, non-blocking, 2026-11-09). US1142 defines a wave boundary (every lane of the wave accepted, none in flight) as the point a session hands off, and US1140's `resume_brief.at_wave_boundary` computes it, but `sprint.py handoff` (US1141) writes the brief whatever the boundary says. Four files outside US1142's Affects still say 'No command writes a handoff' and do not mention the resume brief.

## Steps to Reproduce

1. Open a run with a lane in flight and run `sprint.py handoff`: it writes the brief without naming the in-flight lane as a reason to wait.
2. Grep the skill for 'No command writes a handoff': four files still say it.

## Proposed Fix

Have `sprint.py handoff` refuse (or, under a flag, warn) when `at_wave_boundary` is false, naming the blocking unit; correct the four stale sentences to name `sprint.py handoff` and the resume brief; pin both.

## Acceptance Criteria

- [ ] **AC1** The behaviour described is corrected: From US1142's QA review (qa-seat-US1142-r1, non-blocking, 2026-11-09).
- [ ] **AC2** The proposed fix lands, pinned by a test: Have `sprint.py handoff` refuse (or, under a flag, warn) when `at_wave_boundary` is false, naming the blocking unit; correct the four stale sentences to name...

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-09 | Claude Opus 5.5 | Filed |
