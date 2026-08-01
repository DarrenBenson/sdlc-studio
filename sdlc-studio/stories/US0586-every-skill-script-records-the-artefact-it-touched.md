# US0586: Every skill script records the artefact it touched and the action it performed, per run

> **Status:** Draft
> **Delivers:** CR0515
> **Created:** 2026-08-01
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/lib/sdlc_md.py, .claude/skills/sdlc-studio/scripts/tests/test_sdlc_md.py
> **Epic:** EP0196
> **Points:** 5
> **Persona:** Maya Okafor

## User Story

**As a** {{role}}
**I want** {{capability}}
**So that** {{benefit}}

## Acceptance Criteria

### AC1: a tool that touches an artefact records that it did

- **Given** any skill script that creates or modifies an artefact during an open run
- **When** it completes
- **Then** a ledger entry names the artefact, the action and the tool, so the run holds a record of what was done mechanically rather than by hand
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sdlc_md.py::ToolLedgerTests::test_a_tool_records_the_artefact_it_touched

### AC2: the ledger is per run and does not leak across runs

- **Given** two runs touching the same artefact
- **When** the ledger is read for one of them
- **Then** it holds only that run's entries, so a later close cannot claim credit for an earlier run's tool use
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sdlc_md.py::ToolLedgerTests::test_the_ledger_is_scoped_to_its_run

### AC3: a ledger write never fails the tool that was doing real work

- **Given** a ledger path that cannot be written
- **When** a tool performs its action
- **Then** the action succeeds and the failure is reported, because a bookkeeping fault must not refuse work the operator asked for
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sdlc_md.py::ToolLedgerTests::test_a_ledger_fault_never_fails_the_action

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-01 | sdlc-studio | Created via `new` (deterministic) |
