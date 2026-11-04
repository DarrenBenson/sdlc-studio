# CR-0661: A sprint costs 3.75M priced tokens per point in run five against run four's 1.61M and a norm near 1M, and its per-unit ceremony is the largest share

> **Status:** Proposed
> **Priority:** High
> **Type:** Improvement
> **Affects:** .claude/skills/sdlc-studio/scripts/critic.py, .claude/skills/sdlc-studio/scripts/sprint.py, .githooks/pre-commit, .claude/skills/sdlc-studio/scripts/tests/test_critic.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py
> **Evidence:** run_state.session_tokens at 2026-11-04T09:58Z against the RUN-01M6F74P baseline: priced 660,896,187 - 608,397,992. Builder and reviewer totals from the run's task notifications. D0404.
> **Date:** 2026-11-04
> **Created-by:** sdlc-studio file
> **Raised-by:** claude; human; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-11-04T10:09:54Z

## Summary

2026-11-04, run five (RUN-01M6F74P). After 35 hours the run had delivered 14 points for 52.5M priced tokens (the session meter's delta from the run's baseline), against run four's 1.61M per point and an operator norm of about 50 points in 5 hours. The operator ruled it too costly for anyone to adopt. Measured contributors: builder agents at 280K to 670K tokens per unit, each commit to a hub script running 45 to 77 selected modules for 650 to 1,200 s inside the builder's session, reviewer briefs of 500 to 570 lines read in full, every unit but one deriving the full review tier, two of four units needing a second build and review round, and a per-unit chain of six orchestrator commands (self-check record, brief, record, `verify_ac`, transition, lane return) plus two paperwork commits. Orchestration choices (strict sequence, mid-run questions, a repair briefed on every finding) are recorded in D0404 and fixed there. This CR is for what the tooling itself costs.

## Impact

Every project that runs sprints with sdlc-studio pays this per point. At this rate the operator expects nobody to adopt it.

## Acceptance Criteria

_None yet: add them here, or on the stories `refine` decomposes this into._

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-04 | claude | Raised |
