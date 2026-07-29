# US0556: critic evidence, record and signoff each record a whole batch in one invocation, with the open run as the default scope

> **Status:** Review
> **Delivers:** CR0498
> **Created:** 2026-07-29
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/critic.py, .claude/skills/sdlc-studio/scripts/tests/test_critic.py
> **Epic:** EP0189
> **Points:** 5
> **Persona:** Maya Okafor

## User Story

**As a** an agent recording a sprint's review evidence
**I want** each critic verb to take a whole batch in one call, defaulting to the open run
**So that** recording three facts about nineteen units costs three process spawns rather than fifty-seven

## Acceptance Criteria

### AC1: each verb accepts a batch

- **Given** `critic evidence`, `critic record` and `critic signoff`
- **When** each is invoked with `--units` naming several ids
- **Then** every named unit is written in that one invocation, with the same per-unit result the single-unit form produces
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic.py::BatchFormTests::test_each_verb_records_every_named_unit_in_one_invocation
- **Verified:** yes (2026-07-29)

### AC2: the open run is the default scope

- **Given** an open run with an approved batch and no `--units` supplied
- **When** a verb runs with `--from-run`
- **Then** the batch is read from the open run state, and a run with no open batch is refused rather than defaulting to nothing
- **Preserves:** the single-unit `--unit` form keeps its current behaviour and output, so this story owns the critic.py seam it shares with US0557
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic.py::BatchFormTests::test_the_open_run_is_the_default_scope_and_an_absent_batch_is_refused
- **Verified:** yes (2026-07-29)

### AC3: a repeated unit flag is honoured, never silently reduced

- **Given** `--units` or a repeated `--unit`
- **When** more than one id is supplied
- **Then** every id is acted on, and the count acted on is reported, so the single-valued defect BG0386 records cannot recur in the batch form
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic.py::BatchFormTests::test_every_supplied_id_is_acted_on_and_the_count_is_reported
- **Verified:** yes (2026-07-29)

### AC4: a partial failure names which units were written

- **Given** a batch where one unit cannot be written
- **When** the invocation returns
- **Then** it names which units were written and which were not, and exits non-zero, so a partial batch is never read as a whole one
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic.py::BatchFormTests::test_a_partial_failure_names_the_units_written_and_exits_non_zero
- **Verified:** yes (2026-07-29)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-29 | sdlc-studio | Created via `new` (deterministic) |
| 2026-07-29 | Claude Opus 5 | Groomed: criteria authored against this story's slice, each with an executable Verify line |
