# US1275: The phase runner's group kill in verify_ac does not raise where killpg or SIGKILL is absent

> **Status:** Draft
> **Risk-class:** high
> **Delivers:** CR0719
> **Created:** 2026-11-17
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/verify_ac.py, .claude/skills/sdlc-studio/scripts/tests/test_verify_ac.py
> **Epic:** EP0358
> **Points:** 2
> **Persona:** Abena Osei

## User Story

**As a** Abena Osei
**I want** The phase runner's group kill in verify_ac does not raise where killpg or SIGKILL is absent
**So that** CR0719 is delivered by work that can be planned and checked

## Acceptance Criteria

### AC1: A phase that exits in time returns its code where the group kill is unavailable

- **Given** `os.killpg` and `signal.SIGKILL` both removed from their modules, as on Windows
- **When** the phase runner in `verify_ac.py` runs a command that exits 0 and one that exits 3
- **Then** it returns 0 and 3, raises nothing and leaves the output in the sink file. Fails on: the AttributeError the cleanup raises today, which escapes a suppression that names only OS errors and fails every batched verify run on that platform
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_verify_ac.py::PhaseRunnerWithoutGroupKillTests::test_a_finished_phase_returns_its_exit_code

### AC2: A phase that outlives its time is still ended where the group kill is unavailable

- **Given** the same two attributes removed
- **When** the phase runner runs a command that sleeps past its time limit
- **Then** it returns None, the child process it started is no longer running when the call returns, and nothing is raised. Fails on: a fix that only swallows the AttributeError and leaves the timed-out child running, or a call that never returns
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_verify_ac.py::PhaseRunnerWithoutGroupKillTests::test_a_timed_out_phase_is_ended_and_returns_none

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-17 | sdlc-studio | Created via `new` (deterministic) |
