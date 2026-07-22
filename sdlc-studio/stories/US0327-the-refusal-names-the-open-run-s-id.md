# US0327: The refusal names the open run's id, outcome and batch size, and states both ways forward

> **Status:** Draft
> **Delivers:** CR0401
> **Created:** 2026-07-22
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/lib/run_state.py,.claude/skills/sdlc-studio/scripts/tests/test_run_state.py
> **Epic:** EP0111
> **Points:** 2

## User Story

**As an** operator whose plan has just been refused
**I want** the refusal to name the run standing in the way and both ways past it
**So that** I can act on it without opening `run_state.py` or the state file to work out
which run is open and what may be done about it

## Acceptance Criteria

### AC1: the refusal identifies the run standing in the way

- **Given** an open run with a known id, an `outcome` of `running` and a batch of six
  units
- **When** a disjoint batch is planned with `--write` and refused
- **Then** the refusal text carries that run id, that outcome and the batch size six, so
  the operator identifies the run from the message alone
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_run_state.py::RefusalNamesTheOpenRunTests::test_refusal_states_the_open_run_id_outcome_and_batch_size

### AC2: both ways forward are stated as commands, not as advice

- **Given** the same refusal
- **When** its text is read
- **Then** it names both routes, closing the open run and deliberately re-planning it,
  each as a command that runs as printed, and it names no third route
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_run_state.py::RefusalNamesTheOpenRunTests::test_refusal_states_both_ways_forward_as_runnable_commands

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-22 | sdlc-studio | Created via `new` (deterministic) |
