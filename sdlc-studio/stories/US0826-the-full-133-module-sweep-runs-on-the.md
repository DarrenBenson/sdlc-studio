# US0826: the full 133-module sweep runs on the schedule, and a week with no scheduled run is reported rather than silently skipped

> **Status:** Draft
> **Delivers:** CR0586
> **Created:** 2026-09-16
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .github/workflows/lint.yml, .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/lib/run_state.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py
> **Epic:** EP0253
> **Points:** 3
> **Persona:** Maya Okafor

## User Story

**As a** Maya Okafor
**I want** the full 133-module sweep runs on the schedule, and a week with no scheduled run is reported rather than silently skipped
**So that** CR0586 is delivered by work that can be planned and checked

## Acceptance Criteria

BG0653 is this project's own precedent, recorded in AGENTS.md: a scheduled lane red for three weeks, unread. Moving a blocking lane to a schedule without an answer to "who reads it" repeats it.

### AC1: the full sweep runs weekly and its outcome lands where a reader already looks

- **Given** the scheduled workflow
- **When** the full module-alone sweep completes, green or red
- **Then** its conclusion, sha and date are written to run state, and `sprint.py status` carries one line naming the last sweep, its outcome and its age
- **Mutant:** write the outcome to the job log alone - the reader is then a person who thinks to open Actions, which is exactly BG0653's shape
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::ModuleAloneSweepTests::test_status_names_the_last_sweep_and_its_age

### AC2: a week with no sweep is reported, never read as green

- **Given** a run state whose last recorded sweep is 8 days old, or absent entirely
- **When** `status` renders
- **Then** it names the sweep as STALE with its age, and a sweep that never ran reads UNKNOWN rather than silently absent
- **Mutant:** report only on a recorded red - a scheduled job that stopped firing then looks exactly like a green week
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::ModuleAloneSweepTests::test_a_missing_or_stale_sweep_is_named

### AC3: a red sweep names the pushes that could have caused it

- **Given** a red sweep and the pushes to main since the last green one
- **When** the sweep records its outcome
- **Then** it names the pushes that touched the red module's import closure, so a week of forty pushes is a list of candidates rather than an archaeology task
- **Mutant:** record the red module alone - with three developers and a week's window, the bisect is manual and nobody does it
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::ModuleAloneSweepTests::test_a_red_sweep_names_candidate_pushes

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-09-16 | sdlc-studio | Created via `new` (deterministic) |
