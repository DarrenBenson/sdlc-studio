# CR-0753: The run report compares each role's cache-read share with the project's earlier runs, and the retro names a fall

> **Status:** Proposed
> **Priority:** Medium
> **Type:** Improvement
> **Size:** S
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint_report.py, .claude/skills/sdlc-studio/scripts/retro.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py, .claude/skills/sdlc-studio/scripts/tests/test_retro.py
> **Date:** 2026-11-25
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** RUN-01M89MN1 - raised during the run, 2026-11-25T21:34:16Z

## Summary

The cost anatomy states each role's cache-read and cache-write share for one run; nothing sets it against earlier runs. Cache writes are a large part of the bill: in run twenty-six (RPT0045) they were 33.1M of 146.4M priced tokens, 26 per cent of builder spend and 34 per cent of the other agents', against 10 per cent for the orchestrator. The Claude-in-Foundry cost session recorded on 2026-11-24 (Controlling Claude Costs in Foundry) named the cache-read share as the signal to watch: a fall means a prompt changed and stopped hitting the cache.

Proposed: the report states each role's cache-read share beside its mean over the last five signed runs, and the retro names a fall of more than 10 points as a finding to explain.

## Impact

A change to a brief, a seat charter or the harness that breaks caching raises the cost per point silently: today it shows only as a higher total, with nothing pointing at the cause.

## Acceptance Criteria

_None yet: add them here, or on the stories `refine` decomposes this into._

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-25 | sdlc-studio | Raised |
