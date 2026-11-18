# US1276: The reap in the mutation runner does not raise where killpg or SIGKILL is absent

> **Status:** Draft
> **Risk-class:** elevated
> **Delivers:** CR0719
> **Created:** 2026-11-17
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/mutation.py, .claude/skills/sdlc-studio/scripts/tests/test_mutation.py
> **Epic:** EP0358
> **Points:** 1
> **Persona:** Abena Osei

## User Story

**As a** Abena Osei
**I want** The reap in the mutation runner does not raise where killpg or SIGKILL is absent
**So that** CR0719 is delivered by work that can be planned and checked

## Acceptance Criteria

### AC1: The mutation runner's reap does not raise where the group kill is unavailable

- **Given** `os.killpg` and `signal.SIGKILL` both removed from their modules, as on Windows
- **When** the mutation runner's test run (`_run_tests`) runs a passing command, a failing command and one that outlives its time limit
- **Then** each returns the verdict it returns today with the attributes present, no AttributeError escapes, and the timed-out command's child is no longer running afterwards. Fails on: the reap as it stands, whose suppression names only OS errors, so every mutant's test run raises on that platform
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_mutation.py::ReapWithoutGroupKillTests::test_the_reap_does_not_raise_and_the_verdict_is_unchanged

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-17 | sdlc-studio | Created via `new` (deterministic) |
