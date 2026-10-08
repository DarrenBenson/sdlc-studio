# BG1002: goal-review brief ignores the plan's --serves and the batch changes made after plan --write

> **Status:** Open
> **Severity:** Medium
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_goal_review_brief_live_state.py, changelog.d/BG1002.md
> **Evidence:** homelab RUN-01M4EMNN goal review, 2026-10-08
> **Created:** 2026-10-08
> **Created-by:** sdlc-studio file
> **Raised-by:** sdlc-studio; agent; v1
> **Raised-in-batch:** none open - raised outside a delivery batch, 2026-10-08T21:01:23Z

## Summary

In the homelab consuming project (RUN-01M4EMNN, 2026-10-08) `sprint plan --write --serves "Household Member"` printed 'goal serves: Household Member (Served)', but `sprint goal-review brief` for every seat then said 'Goal serves: NONE - the goal names no PRD outcome or persona' and its 'Personas designed for' list omitted the Household Member entirely (it listed AI Agent, Operator and the declined Platform Collector). The same brief said 'Batch: 14 unit(s)' after two `sprint batch add` calls had made it 16. Seats are therefore briefed against a goal with no served persona and a batch that is not the one under review - BG0277/BG0381's class (the brief derives from a stale snapshot), on two more fields.

## Steps to Reproduce

1. sprint plan --worklist W --write --serves "Household Member" --sprint-goal G
2. sprint batch add BG0266 --reason ...; sprint batch add BG0263 --reason ...
3. sprint goal-review brief --seat product -> 'Goal serves: NONE'; Household Member absent; 'Batch: 14 unit(s)'

## Proposed Fix

Read `serves` and the batch from the live run state (run-state.json), not the plan snapshot; list Served personas in 'Personas designed for' beside Primary/Secondary. Test: plan with --serves, batch add, brief -> names the persona and the new count.

## Acceptance Criteria

- [ ] **AC1** `sprint goal-review brief` names a persona the run declares with `plan --serves` as served, under "Goal serves" and among the personas designed for, whatever the goal's own wording traces to
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_goal_review_brief_live_state.py -k serves_declared_at_plan_reaches_the_brief
- [ ] **AC2** The brief's batch line counts the live run's batch, including units added with `sprint batch add` after `plan --write`
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_goal_review_brief_live_state.py -k batch_line_reads_the_live_run

## Triage

- Confirmed at be92626b by the code path: `_compose_seat_brief` (sprint.py:11059) writes `Batch: {plan['count']}` from the plan snapshot in `.local/sprint-plan.json`, not the run's batch; `_goal_served_lines` traces the goal from its own text (`goal_trace`) and never reads the run's `--serves` declaration, and lists only Primary and Secondary personas, so a Served persona is absent. Pre-existing; BG0277 and BG0381's class (the brief derives from a stale snapshot) on two more fields.
- Severity Medium stands: every seat is briefed against a goal with no served persona and a batch that is not the one under review. Affects corrected to repository paths; tool-derived criteria replaced with two executable ones. Related: CR-0627 (the same brief, per seat).

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-10-08 | sdlc-studio | Filed |
| 2026-10-09 | Claude Opus 5.5 (triage) | Triaged: confirmed by the code path; Affects corrected; criteria made executable |
