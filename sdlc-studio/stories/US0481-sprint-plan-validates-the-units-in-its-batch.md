# US0481: sprint plan validates the units in its batch, not only their index rows

> **Status:** Ready
> **Delivers:** CR0444
> **Created:** 2026-07-27
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py
> **Epic:** EP0173
> **Points:** 5

## User Story

**As a** operator about to commit a batch to a sprint
**I want** the planner to check the units it resolved, not just their index status
**So that** a unit whose declared footprint the workspace contradicts is caught before it is built, not after

## Acceptance Criteria

### AC1: the plan names a batch unit whose Verify targets a file its Affects omits

- **Given** a batch containing a unit whose acceptance criteria verify a file absent from its Affects
- **When** sprint plan runs
- **Then** it names that unit and the missing path in its pre-flight output
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::BatchValidationTests::test_the_plan_names_a_unit_with_an_undeclared_verify_target
- **Verified:** yes (2026-08-05)

### AC2: the scope is the batch, never the corpus

- **Given** a workspace carrying many pre-existing instances in units outside the batch
- **When** a plan whose own units are clean runs
- **Then** it reports nothing and does not refuse, because a defect in work nobody is planning cannot block a plan
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::BatchValidationTests::test_instances_outside_the_batch_do_not_block_the_plan
- **Verified:** yes (2026-08-05)

### AC3: a unit added to an open run afterwards is covered too

- **Given** an open run whose batch is clean
- **When** a unit with an undeclared verify target is added with batch add
- **Then** the same check runs and reports it, so joining a batch late is not a way past the gate
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::BatchValidationTests::test_a_late_added_unit_is_checked_too
- **Verified:** yes (2026-08-05)

### AC4: whether it blocks or warns is configurable and its default is documented

- **Given** the setting absent, set to warn, and set to block
- **When** a plan with an offending unit runs under each
- **Then** the behaviour follows the setting, the shipped default is the one help/sprint.md states, and the help text and the code agree
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::BatchValidationTests::test_block_or_warn_follows_config_and_the_documented_default
- **Verified:** yes (2026-08-05)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-27 | sdlc-studio | Created via `new` (deterministic) |
| 2026-07-27 | Claude Fable 5 | Groomed: acceptance criteria authored against the slice |
