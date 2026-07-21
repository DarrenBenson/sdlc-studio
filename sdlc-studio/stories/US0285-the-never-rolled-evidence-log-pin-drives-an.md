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

The property is behavioural, but the plan-time design for making it cheap was WRONG and the
build falsified it. The plan said to drive the pin with a small injected cap. In fact
`roll_jsonl`'s `max_lines` default binds at definition time, so patching
`DEFAULT_LOG_MAX_LINES` would not change the cap a hypothetical `roll_jsonl(path)` call
applies - a small-cap test would have passed whether or not the log rolled. That is precisely
the vacuous-test class this suite keeps catching, and it would have been introduced by a story
whose stated purpose was to make a test cheaper.

What was built instead keeps the real 5,000 boundary and reaches it in ONE bulk write, then
appends a single record through `record`. The failing condition is identical, it costs 0.04s
rather than 10.1s, and it is sharper: any roll is now attributable to that single call rather
than to somewhere in five thousand.

## Acceptance Criteria

### AC1: the pin reaches the real cap without paying for 5,050 calls

- **Given** an evidence log seeded past the shipped cap in one write
- **When** a single record is appended through the real `record` path
- **Then** the non-roll property is asserted at the real boundary, with the roll attributable
  to that one call
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_telemetry.py::RecordTests::test_the_evidence_log_is_never_rolled
- **Verified:** yes (2026-07-21)

### AC2: both original assertions survive

- **Given** the two assertions the test made before - the record count exceeds the cap, and the
  oldest record is still first
- **When** the rewritten test runs
- **Then** both are still asserted
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_telemetry.py::RecordTests
- **Verified:** yes (2026-07-21)

### AC3: the boundary the pin uses is the boundary a roll would apply

- **Given** `roll_jsonl`, whose `max_lines` default binds at definition time
- **When** that default is read
- **Then** it is asserted to be `DEFAULT_LOG_MAX_LINES`, stating the coupling the pin depends on
  rather than leaving it to be inferred - this is the assertion that makes AC1's choice of the
  real cap load-bearing instead of incidental
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_telemetry.py::RecordTests::test_the_evidence_log_uses_the_shipped_default_cap
- **Verified:** yes (2026-07-21)

### AC4: the rewritten pin can still fail

- **Given** the rewritten test
- **When** a roll is reintroduced into the record path as a mutant
- **Then** the test goes red, proving the cheaper form still reaches the defect it names
- **Measured at delivery (2026-07-21):** `test_telemetry.py` **10.4s -> 0.259s**. Mutant
  applied - `sdlc_md.roll_jsonl(path)` added to `telemetry._append`, so the evidence log rolls
  at the shipped cap - and `test_the_evidence_log_is_never_rolled` FAILED, killing it in
  0.040s. The cheaper form reaches the defect the expensive one named.
- **Verify:** manual apply a roll mutant to the record path and confirm the pin goes red before
  the change is accepted. The cheaper a test gets, the more this matters - L-0140.
- **Verified:** manual

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-21 | sdlc-studio | Created via `new` (deterministic) |
