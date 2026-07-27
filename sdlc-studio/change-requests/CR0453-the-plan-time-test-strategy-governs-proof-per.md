# CR-0453: The plan-time test strategy governs proof per unit but not execution cost, and is printed rather than recorded

> **Status:** Proposed
> **Priority:** High
> **Type:** Improvement
> **Size:** M
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/reference-sprint.md, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py
> **Date:** 2026-07-28
> **Created-by:** sdlc-studio file
> **Raised-by:** Claude Fable 5 (operator-raised, measured on RUN-01KYHVWK); agent; skill v5.0.0

## Summary

A test strategy IS produced at sprint planning: for RUN-01KYHVWK it named the TSD risk areas the batch touched, the proof each unit owed (unit, eval, mutation+unit) and the TSD coverage the batch would not deliver. Two things are wrong with it.

First, it says nothing about EXECUTION. It answers 'what proof does each unit need', never 'what runs, how often, and at what cost'. The per-commit execution policy lives in the hook and is never reconciled with the strategy, so nobody ever proposed - or signed off - the policy that was actually followed. Measured on this run: the full suite executed about 52 times for roughly 218 minutes, against 35 minutes of delivery. The plan said 'BG0305 -> unit'. It never said 'and re-run 4,624 tests fifty-two times'.

Second, the strategy is PRINTED to the terminal and never persisted. `sprint-plan.json` carries the batch, the lane partition, the token forecast and the gate briefing, but no `test_strategy` key. So it cannot be reviewed at plan time, cannot be signed off, and cannot be compared afterwards against what actually ran. A strategy that leaves no record is advice, not a plan.

## Impact

Who: every project running a sprint, and the release decision itself - this is currently the stated blocker on cutting v5. What breaks: the single largest cost in a sprint is set by a policy nobody wrote down, nobody reviewed and nobody agreed. The strategy exists precisely so testing is a decision rather than a habit, and on cost it is silent, so the habit wins. It also makes the waste invisible in the retro: the close reports what was delivered and what it cost in tokens, never that the suite ran 52 times.

## Acceptance Criteria

- [ ] The plan-time test strategy states the EXECUTION policy as well as the proof obligations: what runs per commit, what runs at close, what runs at release, and the estimated cost of each.
- [ ] The strategy is persisted with the plan rather than printed only, so it can be reviewed at plan time, signed off with the goal, and read back afterwards.
- [ ] The close reports execution actuals against that policy - how many full-suite runs happened and what they cost - so a sprint that ran the suite fifty times shows it in the retro rather than hiding it.
- [ ] A strategy whose declared per-commit policy differs from what the hook actually does is reported, so the two cannot silently disagree about the most expensive decision in the sprint.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-28 | Claude Fable 5 (operator-raised, measured on RUN-01KYHVWK) | Raised |
