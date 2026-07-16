# CR-0311: Sprint Goal: a product-outcome goal on the sprint plan, judged at the closing review - the --goal flag is a pipeline stage, not a goal

> **Status:** In Progress
> **Decomposed-into:** EP0053
> **Priority:** Medium
> **Type:** Improvement
> **Size:** S
> **Affects:** .claude/skills/sdlc-studio/reference-sprint.md, .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/sprint_report.py
> **Date:** 2026-07-16
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Fable 5; agent; agile-practice gap analysis 2026-07-16

## Summary

Gap analysis vs proven practice (research sweep 2026-07-16): Scrum Guide 2020 evidence (moderate-strong) is that a single Sprint Goal drives focus and alignment, and its absence is a marker of ceremony-without-intent. sdlc-studio's --goal flag names a pipeline stage, not a product outcome; the plan records a batch and an order, never an intent ('make the estimator honest', 'close the audit's High tier'). Minimal, Maya-shaped fix: sprint plan accepts/prompts one goal sentence recorded on the plan and run-state; the mandatory closing review judges the increment against it (achieved / partially / missed, one line of judgement); `sprint_report` displays it beside delivered/cost. One line of ceremony, no new gate - the review leg that already exists gains the question that makes it a sprint review rather than a batch audit.

## Impact

A sprint batch is currently unified only by ordering (WSJF) and a ladder state (triage/plan/design/done); nothing records WHY this batch, so the closing review can verify every unit Done yet never ask whether the sprint achieved anything coherent.

## Acceptance Criteria

- [ ] sprint plan records an operator-supplied one-line Sprint Goal on the plan and run-state (prompted interactively, --sprint-goal flag headless; optional, absent = recorded as none, never invented)
- [ ] The closing review's verdict includes goal-achievement (achieved/partial/missed + one line) whenever a goal was set
- [ ] `sprint_report.py` show displays the goal and the review's goal verdict beside delivered points and cost

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-16 | Claude Fable 5 | Raised |
