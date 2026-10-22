# CR-0653: A delegated token total supplied for an agent outside this session is dropped whenever the session ran any subagent, because the reading's 'subagents included' flag is per session, not per agent

> **Status:** Proposed
> **Priority:** Low
> **Type:** Feature
> **Affects:** .claude/skills/sdlc-studio/scripts/lib/run_state.py, .claude/skills/sdlc-studio/scripts/sprint_report.py, .claude/skills/sdlc-studio/scripts/retro.py, .claude/skills/sdlc-studio/scripts/tests/test_run_state.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py, .claude/skills/sdlc-studio/scripts/tests/test_retro.py
> **Evidence:** US1091 QA review round 1, 2026-10-22: worth-knowing note.
> **Date:** 2026-10-22
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-10-22T13:54:45Z

## Summary

US1091's AC4 stops adding a supplied delegated total (`sprint.py lane return --tokens N`) when the stamps show the reading includes subagent transcripts. That is right for an agent this harness spawned, whose transcript the meter reads; it is wrong for one run on another machine or another harness, whose spend the meter cannot see. The flag is per session, so any subagent in the session drops every supplied total.

## Impact

A run that mixes in-session and out-of-session agents under-reports the out-of-session spend.

## Acceptance Criteria

_None yet: add them here, or on the stories `refine` decomposes this into._

## Recommendation

Record which delegated totals name an agent the meter can see (a transcript id, or the harness that ran it) and add only the ones it cannot.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-22 | Claude Opus 5.5 | Raised |
