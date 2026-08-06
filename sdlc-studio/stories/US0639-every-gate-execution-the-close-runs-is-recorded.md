# US0639: Every gate execution the close runs is recorded, so the close cost report is not a fraction of the truth

> **Status:** Done
> **Delivers:** CR0510
> **Created:** 2026-08-05
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py,.claude/skills/sdlc-studio/scripts/sprint_report.py,.claude/skills/sdlc-studio/scripts/tests/test_sprint.py,.claude/skills/sdlc-studio/scripts/tests/test_sprint_report.py
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
- **Verified:** yes (2026-08-05)

### AC2: the recorded cost rises with the number of gates actually run

- **Given** two pre-flight runs followed by one chain gate
- **When** `close_cost` is asked for that run
- **Then** it reports three measured runs, not one, and the seconds are their sum
- **Mutant:** filter pre-flight rows out of the cost - the count reads 1 and the seconds under-report
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::CloseCostRecordingTests::test_every_gate_the_close_ran_is_counted
- **Verified:** yes (2026-08-05)

### AC3: an early return that never reached the gate records nothing

- **Given** a pre-flight that returns at the run-state check
- **When** it returns
- **Then** no row is appended, because a gate that did not run must never appear on the ledger as one that did
- **Mutant:** record unconditionally on entry - a run with no gate reports gate seconds
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::CloseCostRecordingTests::test_a_preflight_that_never_reached_the_gate_records_nothing
- **Verified:** yes (2026-08-05)

### AC4: a ledger that cannot be written still does not break the pre-flight

- **Given** an unwritable ledger path
- **When** the pre-flight runs its gate
- **Then** the pre-flight returns its blockers as normal and the failure to record is reported on stderr, not swallowed
- **Mutant:** let the `OSError` propagate - a reporting loss becomes a close that cannot run
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::CloseCostRecordingTests::test_an_unwritable_ledger_warns_and_does_not_break_the_preflight
- **Verified:** yes (2026-08-05)

### AC5: a close --dry-run records nothing at all

- **Given** the one caller whose contract is stricter than the pre-flight's - a preview that must leave the tree byte-identical
- **When** it runs the pre-flight
- **Then** no cost row is appended, and the suppression is an explicit opt-out at that call site while the default stays record
- **Mutant:** record unconditionally - the dry-run tests redden; default the flag to False instead - AC1 reddens. Neither direction passes silently
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::CloseCostRecordingTests::test_the_dry_run_records_no_cost_row
- **Verified:** yes (2026-08-05)

### AC6: the pre-flight's green is never reused by the chain's wider gate

- **Given** a passing pre-flight row on the ledger and an unchanged surface
- **When** the close chain reaches its own gate step
- **Then** it runs the gate rather than reusing that row, because the pre-flight scopes conformance to the run's batch and the chain's gate does not - reusing the narrower verdict for the wider gate is a fail-open
- **Mutant:** treat any non-reuse row as reusable - the chain skips its gate on the strength of a check that judged less
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::CloseCostRecordingTests::test_a_preflight_verdict_is_not_reusable_by_the_chain
- **Verified:** yes (2026-08-05)

### AC7: the shipped verb records it, not only the function (with AC1)

- **Given** an open run
- **When** `sprint.py preflight` is driven as an operator types it
- **Then** exactly one close row is appended, carrying the run id and the `preflight` mode
- **Mutant:** record from `cmd_close` instead of from the pre-flight itself - every function test still passes and this reddens, because a bare `preflight` never reaches a close
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::CloseCostRecordingTests::test_the_shipped_preflight_verb_records_its_gate
- **Verified:** yes (2026-08-05)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-05 | sdlc-studio | Created via `new` (deterministic) |
