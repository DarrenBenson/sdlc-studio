# BG0263: The goal review has no rounds, so rewriting a goal in response to a REJECT erases the fact that it was ever rejected

> **Status:** Fixed
> **Verification depth:** functional - node-addressed tests green, mutation-proven by the delivering worktree agent; merged and re-verified on the composed tree
> **Severity:** Medium
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py
> **Created:** 2026-07-22
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1

## Summary

Found on the first live Sprint Goal review. Three seats reviewed a goal, the engineering seat REJECTED it with three specific defects, the goal was rewritten to answer them, and the seats reviewed the new wording. `goal-review record` holds ONE record: a goal string, a timestamp and a list of seats. The second record overwrote the first.

What is now on disk says three seats reviewed the final goal and broadly accepted it. What actually happened is that the first version was rejected as factually wrong about a sixth of the batch, that its dependency clause was found to be information-free, and that its bar was shown to be satisfiable by 32 trivially-true verifiers. None of that survives, and the surviving record reads as a smooth first-time approval.

The sprint review does not have this problem: `review_rounds` on the run state is a list, each round carries its verdict, and the close can therefore say a sprint took five rounds. The goal review is the same activity one rung earlier and keeps no history at all.

The loss matters most for exactly the case that justifies the ceremony. A goal accepted first time and a goal accepted after being rejected and rewritten are different evidence about how well the batch was understood, and only one of them is recoverable today. This is the same shape as the finding filed as BG0261 about the run's own round ledger: the record smooths the loop out of the history.

## Steps to Reproduce

1. `goal-review record --goal "A" --seat "engineering|no|...|no"`. 2. `goal-review record --goal "B" --seat "engineering|yes|...|yes"`. 3. `goal-review show`. Observed: only the goal-B record exists; the rejection of goal A is gone. Expected: rounds accumulate, as `review_rounds` does for the sprint review, and the plan can report that the goal took N rounds.

## Proposed Fix

Make the record a list of rounds rather than a single object, keyed by the goal string each round judged. The gate keeps its current meaning - the LATEST round must match the goal being planned - so nothing about the wsjf-inputs staleness protection changes. Stamp the round count on the run state alongside `sprint_goal_review` so the close can say what the goal cost to agree.

## Acceptance Criteria

### AC1: the goal review accumulates rounds instead of overwriting

- **Given** a goal reviewed, rejected, reworded, and reviewed again
- **When** the second review is recorded
- **Then** the record holds BOTH rounds (a list, not a single object), the gate reads the
  latest, and the round count reaches the run state - so rewriting a rejected goal no longer
  erases that it was rejected
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::GoalReviewKeepsItsRoundsTests

## Resolution

Goal-review record is now a list of rounds; the gate reads the latest and the round count is
stamped on the run state. Delivered in EP0111's cluster (RUN-01KY5Y3W), mutation-proven by the
delivering agent and re-verified on the composed tree.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-22 | sdlc-studio | Filed |
