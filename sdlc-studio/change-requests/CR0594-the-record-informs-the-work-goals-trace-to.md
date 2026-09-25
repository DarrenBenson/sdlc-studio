# CR-0594: The record informs the work: goals trace to the PRD, and briefs carry the history of the files they touch

> **Status:** In Progress
> **Decomposed-into:** EP0264
> **Merged from:** EP0229, US0740, US0741, US0742, US0743, US0744, CR0529 (backlog sweep 2026-09-24, sdlc-studio/reviews/backlog-sweep-2026-09-24.md)
> **Priority:** High
> **Type:** Improvement
> **Size:** L
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/critic.py, .claude/skills/sdlc-studio/scripts/reconcile.py, sdlc-studio/prd.md, sdlc-studio/trd.md, sdlc-studio/tsd.md, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_critic.py, .claude/skills/sdlc-studio/scripts/tests/test_reconcile.py
> **Date:** 2026-09-24
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch

## Summary

The PRD, TRD and TSD are maintained but almost nothing in the delivery loop reads them: no lane, critic or seat brief opens the PRD or TRD, and the TSD is read only for its test levels. The PRD still describes the pre-lean learning loop. The 889 stories, 261 epics and 754 bugs are read only by hygiene lanes (already-delivered, duplicates); nothing shows a build or review agent the prior Done units and review findings for the files it touches. Recent work was 82% machinery, and no step asks whether a sprint goal serves a PRD outcome. Operator ruling 2026-09-24: lead Sprint 4 with this.

## Impact

Decisions are made without the product record: goals drift to machinery, and agents repeat defects the history already records.

## Acceptance Criteria

- [ ] Given a sprint plan whose goal names no PRD outcome or persona, then the plan flags it as serving none
- [ ] Given the PRD after the refresh, then it describes the lean loop (persona rulings, the one-page report, lesson classes) and no longer describes the retired learning loop as current
- [ ] Given a lane or critic brief for a unit, then it lists, for each file the unit touches, the most recent Done units that changed it with their review findings
- [ ] Given a TRD section on a component a unit touches, then the build brief carries its constraints; a TRD or TSD section nothing reads is cut

## Recommendation

1. sprint plan asks which PRD outcome or persona the goal serves, and the goal seat reads the PRD; a goal that serves none is flagged. 2. Refresh the PRD to describe the lean product, using the unified review against the code. 3. The build and review briefs list, per touched file, the last few Done units that changed it and their review findings, reusing reconcile's already-delivered matcher. 4. TRD architecture constraints reach the build brief for the components touched, and the TSD keeps only what the runner reads; unread sections are cut.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-24 | sdlc-studio | Raised |
