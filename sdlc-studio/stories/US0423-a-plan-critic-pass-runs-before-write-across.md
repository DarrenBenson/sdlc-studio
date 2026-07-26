# US0423: a plan-critic pass runs before --write across the scope, risk and efficiency lenses

> **Status:** Done
> **Delivers:** RFC0050
> **Created:** 2026-07-24
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/critic.py, .claude/skills/sdlc-studio/scripts/tests/test_critic.py
> **Epic:** EP0158
> **Points:** 5

## User Story

**As a** {{role}}
**I want** {{capability}}
**So that** {{benefit}}

## Acceptance Criteria

### AC1: the pass runs before --write across three lenses

- **Given** a plan about to be written
- **When** the plan critic runs
- **Then** it produces findings under the scope, risk and efficiency lenses BEFORE the run is opened - a critique delivered after --write is a critique of a decision already taken
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic.py::PlanCriticTests::test_three_lenses_run_before_the_plan_is_written
- **Verified:** yes (2026-07-24)

### AC2: each lens can find nothing without the pass reading as skipped

- **Given** a batch where one lens has no finding
- **When** the pass completes
- **Then** that lens reports explicitly that it found nothing, distinct from not having run - the distinction the mutation lane had to learn
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic.py::PlanCriticTests::test_a_lens_with_no_finding_is_distinct_from_a_lens_that_did_not_run
- **Verified:** yes (2026-07-24)

### AC3: a refused plan leaves nothing written

- **Given** a plan critic pass that fails partway
- **When** the planner is inspected
- **Then** no run is opened and no plan file is written - the ordering defect BG0268 created and its mirror image both came from a write that outlived its refusal
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic.py::PlanCriticTests::test_a_failed_pass_leaves_no_run_and_no_plan_file
- **Verified:** yes (2026-07-24)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-24 | sdlc-studio | Created via `new` (deterministic) |
