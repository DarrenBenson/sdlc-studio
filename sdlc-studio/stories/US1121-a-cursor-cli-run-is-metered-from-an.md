# US1121: A Cursor CLI run is metered from an afterAgentResponse hook ledger, and the meter reads it as measured

> **Status:** Ready
> **Delivers:** CR0662
> **Created:** 2026-11-05
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/lib/meter_cursor.py, .claude/skills/sdlc-studio/scripts/cursor_usage_hook.py, .claude/skills/sdlc-studio/scripts/tests/test_meter_cursor.py, .claude/skills/sdlc-studio/reference-sprint.md, changelog.d/US1121.md
> **Epic:** EP0274
> **Points:** 3
> **Persona:** Maya Okafor

## User Story

**As a** Maya Okafor
**I want** A Cursor CLI run is metered from an afterAgentResponse hook ledger, and the meter reads it as measured
**So that** a sprint driven by the Cursor CLI reads a measured cost

## Acceptance Criteria

- **AC1:** Given a ledger of `afterAgentResponse` payloads appended by `cursor_usage_hook.py`, when the Cursor CLI meter reads a run window, then it returns the window's summed input, output, cache-read and cache-write tokens with their priced cost, and reads the run as measured with a basis naming the ledger
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_meter_cursor.py::CursorHookLedgerTests::test_the_ledger_is_read_as_measured
- **AC2:** Given no ledger, then the CLI reading stays not attributable with its reason as before; given a malformed ledger line, it is skipped and counted in the reading, not fatal
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_meter_cursor.py::CursorHookLedgerTests::test_no_ledger_stays_unattributable_and_a_bad_line_is_counted
- **AC3:** Given `reference-sprint.md`, then it names the hook entry that writes the ledger and the path the meter reads it from
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_meter_cursor.py::CursorHookLedgerTests::test_the_reference_names_the_hook_and_ledger

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-05 | sdlc-studio | Created via `new` (deterministic) |
