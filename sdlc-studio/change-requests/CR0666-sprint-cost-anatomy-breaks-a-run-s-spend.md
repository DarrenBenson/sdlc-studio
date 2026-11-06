# CR-0666: sprint cost --anatomy breaks a run's spend down by role and names what drove it

> **Status:** Complete
> **Decomposed-into:** EP0299
> **Parent:** RFC0062
> **Priority:** High
> **Type:** Feature
> **Size:** M
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/lib/run_state.py, .claude/skills/sdlc-studio/scripts/sprint_report.py, .claude/skills/sdlc-studio/reference-sprint.md, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_run_state.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py
> **Evidence:** RFC0062 Phase 1; run six's transcripts and the 2026-11-06 capture of one headless session per CLI harness.
> **Date:** 2026-11-06
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Opus 5.5; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-06T11:17:48Z

## Summary

RFC0062's review needs to see where a run's tokens went. Run six's breakdown (orchestrator 40%, builders 34%, reviewers 21%, repairs 5%; cache reads 70%; a 40k starting context in every subagent) was computed by a one-off script. It belongs in the shipped tooling, so every run reports it and a regression is visible.

## Impact

The operator and the review cannot tell which role, step or tool output is driving a run's cost without hand analysis of transcripts.

## Acceptance Criteria

- [ ] sprint.py cost --anatomy prints, for the open run or a named one, per role (orchestrator, builder, reviewer, repair, other): agents, calls, priced tokens and share, the cache-read, cache-write and output split, the starting context and the average context per call
- [ ] It names the ten tool outputs that cost most, each costed as its size times the calls that re-read it, with the command or file that produced it
- [ ] A subagent's role comes from the run's own lane and review records, not from its prompt text
- [ ] A harness whose store holds no per-call context reports those columns as not available, never as zero
- [ ] The sprint report's cost section carries the per-role table

## Recommendation

Read the same transcripts the meter reads, keyed by the agent ids lane return and lane accept already record.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-06 | Claude Opus 5.5 | Raised |
