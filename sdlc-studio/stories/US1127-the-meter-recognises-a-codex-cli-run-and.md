# US1127: The meter recognises a Codex CLI run and reads its token actual from the Codex store

> **Status:** Ready
> **Delivers:** CR0668
> **Created:** 2026-11-06
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/lib/meter_codex.py, .claude/skills/sdlc-studio/scripts/lib/token_meters.py, .claude/skills/sdlc-studio/scripts/tests/test_meter_codex.py, .claude/skills/sdlc-studio/scripts/tests/test_token_meters.py, .claude/skills/sdlc-studio/reference-sprint.md, changelog.d/US1127.md
> **Epic:** EP0299
> **Points:** 3
> **Persona:** Maya Okafor

## User Story

**As a** Maya Okafor
**I want** The meter recognises a Codex CLI run and reads its token actual from the Codex store
**So that** a sprint driven from Codex CLI records its token actual

## Acceptance Criteria

- **AC1:** Given a fixture Codex store built from a real captured session and `SDLC_STUDIO_HARNESS=codex`, when the meter reads, then the total counts input, output and cache write with cache reads apart, and cached input is split out of input. Fails on: cached input counted twice
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_meter_codex.py::CodexMeterTests::test_reads_the_captured_session
- **AC2:** Given no `SDLC_STUDIO_HARNESS`, then the Codex reader is chosen by an environment variable a real Codex session sets, established from a captured session, and `codex` is listed in `token_meters.HARNESSES`. Fails on: a signal taken from documentation that a real session does not set
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_meter_codex.py::CodexMeterTests::test_selected_by_the_codex_session_signal
- **AC3:** Given a missing, locked or unreadable store, then the reading has tokens None and names why, and the store is only ever opened read-only. Fails on: a read-write open, or a missing store read as zero
  - **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_meter_codex.py::CodexMeterTests::test_missing_or_unreadable_store_is_named_and_read_only

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-06 | sdlc-studio | Created via `new` (deterministic) |
| 2026-11-06 | Claude Opus 5.5 | Groomed: criteria and Verify checks authored for run seven (RFC0062 Phase 1) |
