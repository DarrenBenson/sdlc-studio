# US1259: lessons reinstate returns a retired class to active with the open run and a reason, refusing a class that is not retired

> **Status:** Draft
> **Risk-class:** standard
> **Delivers:** CR0709
> **Created:** 2026-11-17
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/lessons.py, .claude/skills/sdlc-studio/scripts/tests/test_lessons.py, .claude/skills/sdlc-studio/help/lessons.md, .claude/skills/sdlc-studio/reference-scripts-surface.md, sdlc-studio/reviews/command-audit.md
> **Epic:** EP0349
> **Points:** 3
> **Persona:** Abena Osei

## User Story

**As a** Abena Osei
**I want** lessons reinstate returns a retired class to active with the open run and a reason, refusing a class that is not retired
**So that** CR0709 is delivered by work that can be planned and checked

## Acceptance Criteria

### AC1: Reinstating a retired class puts it back in force with the run and the reason

- **Given** a store holding a retired class with a `retired_run`, another class beside it, and a run open
- **When** `lessons.py reinstate --class <LC code> --reason <why>` is run
- **Then** the class's row reads `state` active, has no `retired_run`, carries `reinstated_run` as the open run's id and `reinstated_reason` as the reason given, its `hits` are unchanged, and every other row is byte-identical. Fails on: a hit recorded to bring the class back, a `retired_run` left on an active row, or a neighbouring row rewritten
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lessons.py::ReinstateTests::test_a_retired_class_returns_to_active_with_the_open_run_and_reason

### AC2: A class that is not retired, or a blank reason, is refused

- **Given** a store holding an active class, a graduated class and a retired class
- **When** `reinstate` is run on the active class, on the graduated class, on a code the store does not hold, and on the retired class with a blank `--reason`
- **Then** each exits non-zero naming the class and the state it is in (or that it is unknown, or that the reason is blank) and the store is byte-identical afterwards; the retired class with a reason, run beside them, succeeds. Fails on: an active or graduated row stamped as reinstated, or a reinstatement recorded with no reason
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lessons.py::ReinstateTests::test_a_class_not_retired_or_a_blank_reason_is_refused_with_the_store_unchanged

### AC3: With no run open the reinstatement is still recorded, and an unreadable run state refuses

- **Given** a retired class, first with no run open and then with a run state file that cannot be read
- **When** `reinstate` is run in each
- **Then** with no run open the class returns to active with its reason and an empty `reinstated_run`, as `class-add` stamps `recorded_run`, and the output says no run was open; with the unreadable run state it is refused and the store is unchanged. Fails on: a run id invented outside a run, or a class reinstated against a run state the tool could not read
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lessons.py::ReinstateTests::test_no_open_run_records_an_empty_run_and_an_unreadable_state_refuses

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-17 | sdlc-studio | Created via `new` (deterministic) |
