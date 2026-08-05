# US0639: Every gate execution the close runs is recorded, so the close cost report is not a fraction of the truth

> **Status:** Ready
> **Delivers:** CR0510
> **Created:** 2026-08-05
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py,.claude/skills/sdlc-studio/scripts/tests/test_sprint.py
> **Epic:** EP0208
> **Points:** 2
> **Persona:** Maya Okafor

## User Story

**As a** Maya Okafor
**I want** Every gate execution the close runs is recorded, so the close cost report is not a fraction of the truth
**So that** CR0510 is delivered by work that can be planned and checked

## Acceptance Criteria

### AC1: a pre-flight gate run appends its own ledger row

- **Given** an open run and a pre-flight that reaches the gate
- **When** it runs
- **Then** a `close` row is appended carrying measured seconds, the run id, and a mode distinguishing it from the chain's own gate run
- **Mutant:** drop the record call - the ledger holds no row for a gate that demonstrably ran
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::CloseCostRecordingTests::test_a_preflight_gate_run_is_recorded_with_its_seconds

### AC2: the recorded cost rises with the number of gates actually run

- **Given** two pre-flight runs followed by one chain gate
- **When** `close_cost` is asked for that run
- **Then** it reports three measured runs, not one, and the seconds are their sum
- **Mutant:** filter pre-flight rows out of the cost - the count reads 1 and the seconds under-report
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::CloseCostRecordingTests::test_every_gate_the_close_ran_is_counted

### AC3: an early return that never reached the gate records nothing

- **Given** a pre-flight that returns at the run-state check
- **When** it returns
- **Then** no row is appended, because a gate that did not run must never appear on the ledger as one that did
- **Mutant:** record unconditionally on entry - a run with no gate reports gate seconds
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::CloseCostRecordingTests::test_a_preflight_that_never_reached_the_gate_records_nothing

### AC4: a ledger that cannot be written still does not break the pre-flight

- **Given** an unwritable ledger path
- **When** the pre-flight runs its gate
- **Then** the pre-flight returns its blockers as normal and the failure to record is reported on stderr, not swallowed
- **Mutant:** let the `OSError` propagate - a reporting loss becomes a close that cannot run
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::CloseCostRecordingTests::test_an_unwritable_ledger_warns_and_does_not_break_the_preflight

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-05 | sdlc-studio | Created via `new` (deterministic) |
