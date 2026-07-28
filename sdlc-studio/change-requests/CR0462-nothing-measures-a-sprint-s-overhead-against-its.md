# CR-0462: Nothing measures a sprint's overhead against its delivery, so a 9:1 ratio took an operator noticing

> **Status:** In Progress
> **Decomposed-into:** EP0179
> **Priority:** High
> **Type:** Improvement
> **Size:** M
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint_report.py, .claude/skills/sdlc-studio/scripts/sprint.py, sdlc-studio/retros/VELOCITY.md
> **Date:** 2026-07-28
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Fable 5 (RUN-01KYJZGZ retro, four inert mechanisms); agent; skill v5.0.0

## Summary

The close reports what was delivered and what it cost in tokens. It does not report the ratio that actually matters to whether the discipline is worth running: time spent on the process versus time spent on the work. On RUN-01KYHVWK that ratio was about 9:1 - 35 minutes of delivery against roughly 316 minutes of gate, review and re-running - and it surfaced only because the operator said it felt slow and I measured it by hand. On RUN-01KYJZGZ the dominant line moved entirely, from 52 full-suite runs to repair cycles caused by rejected deliveries, and that also had to be worked out by hand afterwards.

## Impact

Who: every operator deciding whether to keep using this, which is the adoption decision. What breaks: the product's core claim is that it saves time, and the one number that would falsify or support that claim is the one thing never recorded. A cost that is not measured cannot be managed, and the two sprints where it was measured both found the dominant line somewhere nobody expected.

## Acceptance Criteria

- [ ] The close reports delivery time against overhead time - gate, review, re-runs and repair cycles - as a ratio, alongside the points and token figures it already carries.
- [ ] The figures are derived from what the run recorded rather than estimated at close, and a component that was not measured is reported as unmeasured rather than as zero.
- [ ] The ratio is written to the velocity record so the trend across sprints is visible, since a single sprint's ratio says little and the direction says everything.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-28 | Claude Fable 5 (RUN-01KYJZGZ retro, four inert mechanisms) | Raised |
