# US0285: The never-rolled evidence-log pin drives an injected cap, not 5,050 real records

> **Status:** Draft
> **Created:** 2026-07-21
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/tests/test_telemetry.py
> **Epic:** EP0093
> **Points:** 2
> **Persona:** repo maintainer (dogfooding operator)

## User Story

**As a** repo maintainer running the gate on every commit
**I want** the never-rolled pin to prove its property at a cap it chooses
**So that** a 10-second test becomes a millisecond one without weakening what it asserts

## Context

`test_the_evidence_log_is_never_rolled` is 10.12s of `test_telemetry.py`'s 10.4s. It writes
`DEFAULT_LOG_MAX_LINES + 50` records one at a time - 5,050 calls to `tel.record` - to show that
the evidence log keeps everything and the oldest record survives.

The property is behavioural and has nothing to do with the cap being 5,000. `roll_jsonl`
already takes `max_lines` as a parameter, so a small cap drives the same assertion. The one
thing a smaller cap could hide is a change to the shipped default, so that gets its own cheap
assertion rather than being left implicit.

## Acceptance Criteria

### AC1: the pin drives an injected cap

- **Given** a small injected cap rather than the shipped 5,000
- **When** more records than the cap are written
- **Then** the same non-roll property is asserted
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_telemetry.py::RecordTests::test_the_evidence_log_is_never_rolled

### AC2: both original assertions survive

- **Given** the two assertions the test made before - the record count exceeds the cap, and the
  oldest record is still first
- **When** the rewritten test runs
- **Then** both are still asserted
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_telemetry.py::RecordTests

### AC3: a smaller test cap cannot mask a change to the real one

- **Given** the shipped `DEFAULT_LOG_MAX_LINES`
- **When** the evidence log's own cap is read
- **Then** it is asserted to be the shipped default, so lowering the cap inside the test cannot
  hide someone lowering it in the product
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_telemetry.py::RecordTests::test_the_evidence_log_uses_the_shipped_default_cap

### AC4: the rewritten pin can still fail

- **Given** the rewritten test
- **When** a roll is reintroduced into the record path as a mutant
- **Then** the test goes red, proving the cheaper form still reaches the defect it names
- **Verify:** manual apply a roll mutant to the record path and confirm the pin goes red before
  the change is accepted. The cheaper a test gets, the more this matters - L-0140.
- **Verified:** manual

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-21 | sdlc-studio | Created via `new` (deterministic) |
