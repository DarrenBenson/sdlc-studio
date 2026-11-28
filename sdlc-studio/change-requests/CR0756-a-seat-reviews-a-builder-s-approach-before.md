# CR-0756: A seat reviews a builder's approach before it writes code, so the first code review judges work built to an agreed plan

> **Status:** Complete
> **Decomposed-into:** EP0385
> **Priority:** High
> **Type:** Feature
> **Size:** M
> **Affects:** .claude/skills/sdlc-studio/scripts/critic.py, .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/lib/lanes.py, .claude/skills/sdlc-studio/templates/config-defaults.yaml, .claude/skills/sdlc-studio/reference-config.md, .claude/skills/sdlc-studio/help/sprint.md, .claude/skills/sdlc-studio/reference-sprint-toolchain.md, .claude/skills/sdlc-studio/scripts/sprint_report.py, .claude/skills/sdlc-studio/scripts/tests/test_critic.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py
> **Evidence:** run twenty-eight (RUN-01M8B7DJ) wave one: BG1764, BG1765, US1332, US1333, US1339, US1340 and US1233 all rejected in round one, US1334 blocked twice on criteria; the operator's direction D0646
> **Date:** 2026-11-26
> **Created-by:** sdlc-studio file
> **Raised-by:** orchestrator; agent; claude-opus-5-5
> **Raised-in-batch:** RUN-01M8B7DJ - raised during the run, 2026-11-26T08:21:40Z

## Summary

Before a builder writes code for a unit, it writes a short approach note: how it reads each criterion's key terms, the design, the existing tests and pages its change may break, the test it will write for each criterion and the mutant each must kill, and the sentences it will state on pages, fragments and the commit message. A review seat checks the note against the criteria, the decisions that bind the unit and the repository, spot-checking by execution, and returns go or a list of changes. The builder then builds to the agreed approach. The code review stays a fresh context that never saw the note, so agreeing the plan cannot anchor the verdict. A project chooses which units take the step (by points and risk class), and the run report shows first-round approval and rounds per unit, so the saving can be measured.

## Impact

Every project that runs sprint lanes. In run twenty-eight's first wave every first review was rejected; about half were approach misses (a criterion's noun read narrowly, a setting the project never set, a criterion that could not hold beside an existing test) that cost a repair builder, a land and a second review each, the largest share of cost per point. A review before code catches them for a fraction of a unit's cost.

## Acceptance Criteria

_None yet: add them here, or on the stories `refine` decomposes this into._

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-26 | orchestrator | Raised |
