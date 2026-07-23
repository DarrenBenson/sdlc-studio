# US0326: sprint plan --write refuses a disjoint batch against an open run, exiting non-zero with run-state.json byte-identical

> **Status:** Review
> **Depends on:** BG0265, BG0256
> **Delivers:** CR0401
> **Created:** 2026-07-22
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/lib/run_state.py,.claude/skills/sdlc-studio/scripts/sprint.py,.claude/skills/sdlc-studio/scripts/tests/test_run_state.py
> **Epic:** EP0111
> **Points:** 5

## User Story

**As an** operator with one sprint already open and a second, unrelated batch to run
**I want** `sprint plan --write` to refuse the disjoint batch instead of fusing it into
the run already open
**So that** the open run keeps its goal, forecast and telemetry, and I learn the tool
holds one run slot at plan time rather than at a close whose verdict cannot be given

## Acceptance Criteria

### AC1: a disjoint batch is refused and run-state.json is byte-identical afterwards

- **Given** an open run holding a six-unit batch under its own Sprint Goal
- **When** `sprint plan --write` is run for a batch sharing no unit with it
- **Then** the command exits non-zero and the bytes of
  `sdlc-studio/.local/run-state.json` are identical before and after, compared by
  digest rather than by field, so no partial write survives the refusal
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_run_state.py::DisjointBatchIsRefusedTests::test_a_disjoint_plan_exits_non_zero_and_leaves_run_state_json_byte_identical
- **Verified:** yes (2026-07-23)

### AC2: overlap decides it, and a genuine re-plan still accumulates with no new flag

- **Given** the same open run
- **When** a batch sharing exactly one unit with it is planned with `--write`, and then
  a batch sharing none, neither passing any flag the command does not have today
- **Then** the first exits zero and leaves the accumulated union under the unchanged
  `run_id` and `started_at`, and the second is refused
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_run_state.py::DisjointBatchIsRefusedTests::test_one_shared_unit_re_plans_and_zero_shared_units_refuses
- **Verified:** yes (2026-07-23)

### AC3: the refused path mints nothing and archives nothing

- **Given** an open run and a disjoint incoming batch
- **When** the plan is refused
- **Then** `.local/run-archive/` gains no entry, no new run id is minted, and the run
  still carries the id it had, so a refusal can never cost the operator the run it was
  protecting
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_run_state.py::DisjointBatchIsRefusedTests::test_a_refused_plan_archives_nothing_and_mints_no_run_id
- **Verified:** yes (2026-07-23)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-22 | sdlc-studio | Created via `new` (deterministic) |
