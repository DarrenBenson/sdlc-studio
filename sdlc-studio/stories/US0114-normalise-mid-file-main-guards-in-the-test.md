# US0114: Normalise mid-file main guards in the test suite

> **Status:** Done
> **Created:** 2026-07-10
> **Created-by:** sdlc-studio new
> **Epic:** EP0026
> **Persona:** repo maintainer (dogfooding operator)
> **CR:** CR0204

## User Story

**As a** test-suite maintainer
**I want** every `if __name__` guard at true end-of-file and a guard that keeps it there
**So that** a direct `python3 test_x.py` run never silently drops classes (22 were dropped and reported OK) and agent appends never truncate files again

## Context

RV0007: eleven test files keep test classes after a mid-file `if __name__` guard; a direct
run executes only the classes above the guard and reports OK; an agent's `rfind`-append once
truncated `test_validate.py` (16 methods lost). The RETRO0016 lesson was recorded but the
layouts were never normalised - and this sprint had to layout-check every append.

## Acceptance Criteria

### AC1: every guard sits at true end-of-file

- **Given** the test suite under `.claude/skills/sdlc-studio/scripts/tests/`
- **When** any test file contains `if __name__`
- **Then** nothing but the guard body follows it (no classes or functions after)
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_repo_hygiene.py -k guard
- **Verified:** yes (2026-07-10)

### AC2: direct-run counts equal discover counts

- **Given** the normalised files
- **When** `python3 <file>` runs any previously-affected file
- **Then** it executes the same test count unittest discover finds for that file
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_repo_hygiene.py -k direct_run
- **Verified:** yes (2026-07-10)

### AC3: the layout cannot regress

- **Given** a future test file with a class after its guard
- **When** the suite runs
- **Then** a hygiene test fails naming the file
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_repo_hygiene.py -k guard
- **Verified:** yes (2026-07-10)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-10 | sdlc | Created via `new` (deterministic) |
| 2026-07-10 | sprint (CR0204 decomposition) | ACs authored; regression guard included |
