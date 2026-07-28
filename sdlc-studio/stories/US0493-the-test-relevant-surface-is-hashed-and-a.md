# US0493: The test-relevant surface is hashed, and a run whose surface is unchanged since the last green verdict is skipped with that verdict reused

> **Status:** Review
> **Delivers:** CR0451
> **Created:** 2026-07-28
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/gate.py, .claude/skills/sdlc-studio/scripts/tests/test_gate.py
> **Epic:** EP0177
> **Points:** 5
> **Persona:** Maya Okafor

## User Story

**As a** maintainer whose commit changed no code at all
**I want** the suite skipped when the test-relevant surface is identical to the last green run
**So that** consecutive paperwork commits and a retried close cost nothing, instead of paying the full price for a tree the tests already passed on

## Acceptance Criteria

### AC1: an unchanged surface reuses the last green verdict

- **Given** a recorded green verdict and a tree whose test-relevant surface hashes identically
- **When** the gate runs
- **Then** it reports the reused verdict and runs no tests, naming the run it is reusing so the decision is visible rather than silent
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_gate.py::SurfaceHashTests::test_an_unchanged_surface_reuses_the_last_green_verdict

### AC2: any change to the surface forces a real run

- **Given** a recorded green verdict and a one-character edit to a source file in the surface
- **When** the gate runs
- **Then** the hash differs and the suite executes, so the cache can never mask a change
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_gate.py::SurfaceHashTests::test_a_changed_surface_forces_a_real_run

### AC3: the hash covers the tests themselves, not only the source

- **Given** an edit to a test file with no source change
- **When** the gate runs
- **Then** the suite executes, because a changed assertion is a changed question even when the answer's code is untouched
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_gate.py::SurfaceHashTests::test_editing_a_test_forces_a_run

### AC4: a verdict that cannot be read is not a pass

- **Given** an absent, unreadable or malformed verdict record
- **When** the gate runs
- **Then** it runs the suite rather than reusing nothing, so a broken cache degrades to the slow answer and never to a false green
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_gate.py::SurfaceHashTests::test_an_unreadable_verdict_runs_the_suite

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-28 | sdlc-studio | Created via `new` (deterministic) |
| 2026-07-28 | Claude Fable 5 | Groomed against the operator's two policy rules |
