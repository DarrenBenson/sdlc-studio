# US0497: The plan-time test strategy states the execution policy - what runs per commit, at close and at release, with its estimated cost

> **Status:** Review
> **Delivers:** CR0453
> **Created:** 2026-07-28
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py
> **Epic:** EP0177
> **Points:** 3
> **Persona:** Maya Okafor

## User Story

**As a** operator reviewing what a sprint will cost before it runs
**I want** the test strategy to state the execution policy and its estimated cost, not only the proof each unit owes
**So that** the largest cost in the sprint is a decision I can see and change, instead of a habit set in a hook

## Acceptance Criteria

### AC1: the strategy names what runs at each moment and its cost

- **Given** a planned batch
- **When** the plan prints its test strategy
- **Then** it states the per-commit mode, the boundary runs, and an estimated cost for each, alongside the per-unit proof obligations it already carries
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::TestStrategyPolicyTests::test_the_strategy_states_the_execution_policy_and_cost

### AC2: a policy that disagrees with the hook is reported

- **Given** a declared per-commit policy and a hook that does something else
- **When** the plan runs
- **Then** the divergence is reported, because the two cannot silently disagree about the most expensive decision in the sprint
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::TestStrategyPolicyTests::test_a_policy_diverging_from_the_hook_is_reported

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-28 | sdlc-studio | Created via `new` (deterministic) |
| 2026-07-28 | Claude Fable 5 | Groomed |
