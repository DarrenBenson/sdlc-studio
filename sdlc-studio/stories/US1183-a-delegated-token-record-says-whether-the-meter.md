# US1183: A delegated token record says whether the meter can see its agent, by transcript or by the harness that ran it

> **Status:** Draft
> **Risk-class:** high
> **Delivers:** CR0653
> **Created:** 2026-11-17
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/lib/run_state.py, .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_delegated_agent_visibility.py
> **Epic:** EP0322
> **Points:** 3
> **Persona:** Abena Osei

## User Story

**As a** Abena Osei
**I want** A delegated token record says whether the meter can see its agent, by transcript or by the harness that ran it
**So that** CR0653 is delivered by work that can be planned and checked

## Acceptance Criteria

### AC1: A total read from this session's agent transcript is recorded as seen by the meter

- **Given** an open run and a builder agent whose transcript is in this session's subagents directory
- **When** `sprint.py lane return <unit> --agent <id>` records its total
- **Then** the delegated record on the run says the meter can see this agent and names the transcript it was read from. Fails on: a record that carries no statement of whether the meter sees it, which is every record today
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_delegated_agent_visibility.py::DelegatedAgentVisibilityTests::test_an_agent_with_a_session_transcript_is_recorded_as_seen

### AC2: A total for an agent another harness ran is recorded as unseen, naming the harness

- **Given** an open run metered by Claude
- **When** `sprint.py lane return <unit> --tokens N --harness codex` records a supplied total, and a `lane run` session in another CLI is priced on return
- **Then** each record says the meter cannot see the agent and names the harness that ran it. Fails on: an out-of-session agent's record indistinguishable from an in-session one, so the report cannot tell which to add
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_delegated_agent_visibility.py::DelegatedAgentVisibilityTests::test_an_agent_another_harness_ran_is_recorded_as_unseen

### AC3: A total that names neither a transcript nor a harness makes no claim

- **Given** `sprint.py lane return <unit> --tokens N` with no `--agent` and no `--harness`, and a run record written before this field existed
- **When** the records are read back through `run_state.delegated_records`
- **Then** both read as not stated: neither seen nor unseen, with the older record returned as it was stored. Fails on: an unstated record defaulting to seen, which drops its total, or to unseen, which counts an in-session agent twice
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_delegated_agent_visibility.py::DelegatedAgentVisibilityTests::test_a_total_naming_neither_is_recorded_as_not_stated

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-17 | sdlc-studio | Created via `new` (deterministic) |
