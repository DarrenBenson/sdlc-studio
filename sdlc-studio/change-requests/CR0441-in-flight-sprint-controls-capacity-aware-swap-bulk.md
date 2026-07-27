# CR-0441: In-flight sprint controls: capacity-aware swap, bulk add by epic, and a resizable appetite

> **Status:** In Progress
> **Decomposed-into:** EP0171
> **Priority:** High
> **Type:** Improvement
> **Size:** M
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/help/sprint.md, .claude/skills/sdlc-studio/reference-sprint.md
> **Date:** 2026-07-27
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Fable 5 (operator-raised, RFC0057 discussion); agent; skill v5.0.0

## Summary

A running sprint can be mutated only one unit at a time and entirely blind to size: `sprint batch add <id>` and `batch drop <id> --reason` never read points, never compare against the appetite the plan was sized to, and report nothing about what the change did to capacity. There is no way to add an epic's stories in one move, and the appetite is fixed when the plan is written with no verb to change it. So the three things an operator actually asks for mid-sprint - bring this story in and take something of similar size out, make the sprint bigger and pull the epic in, rebalance after the work raised three new bugs - are either impossible or are two blind calls the tool cannot tell you preserved anything.

## Impact

Who: every operator running a sprint that meets reality, which is every sprint - a cycle generates bugs and lessons by design, so the batch that was right at planning time rarely stays right. What breaks: the operator adjusts by hand and the run's own record cannot say whether capacity still holds, so the appetite becomes a number that was true once. A swap that quietly doubles the committed points is indistinguishable from one that balanced, and the end-of-sprint report measures delivery against an appetite nobody could keep honest. It also blocks something larger: RFC0057 shows that queueing sprints is only defensible if the running sprint can absorb what the work generates, so a capacity-blind batch is the precondition failure under that whole design.

## Acceptance Criteria

- [ ] batch add and drop report the capacity effect of the change - the unit's points, the batch total before and after, and the appetite it is now measured against - so a mutation is never silent about what it did to the plan.
- [ ] A swap is one operation: bringing a unit in while taking named units out is a single call that reports whether the point totals balanced, and warns when they did not, rather than requiring two calls that cannot see each other.
- [ ] An epic can be added in one move, adding its plannable stories as a set and reporting the combined points against the appetite rather than requiring one call per story.
- [ ] The appetite can be changed on an open run, recorded with a reason on the run state, so making a sprint bigger is a stated decision with a trail rather than a number silently exceeded.
- [ ] A batch change that takes the committed points past the appetite is reported plainly at the moment it happens; it is not refused, because an operator may knowingly overcommit, but it is never silent.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-27 | Claude Fable 5 (operator-raised, RFC0057 discussion) | Raised |
