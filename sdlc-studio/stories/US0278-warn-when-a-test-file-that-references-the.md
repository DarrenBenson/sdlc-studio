# US0278: Warn when a test file that references the target module falls outside the test command's selection

> **Status:** Done
> **Delivers:** CR0363
> **Created:** 2026-07-20
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/mutation.py
> **Epic:** EP0091
> **Depends on:** US0277
> **Points:** 3

## User Story

**As a** consumer of the mutation gate
**I want** a warning when my test command misses tests that exercise the target
**So that** a narrow command cannot manufacture survivors silently

## Acceptance Criteria

### AC1: an out-of-selection referencing test file is named as a warning

- **Given** a test file that references the target module but falls outside the test command's
  selection
- **When** the run completes
- **Then** that file is named in a warning, because unexercised coverage is the
  manufactured-survivor condition
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_mutation.py -k test_warns_on_referencing_test_file_outside_selection
- **Verified:** yes (2026-07-20)

### AC2: the warning is advisory and never blocks

- **Given** the same deliberately narrow run
- **When** the warning fires
- **Then** the exit code and the killed/survived verdicts are unchanged - a narrow run stays
  legal and stays honest about what it covered
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_mutation.py -k test_selection_warning_never_blocks
- **Verified:** yes (2026-07-20)

### AC3: a covering selection produces no warning

- **Given** a test command whose selection includes every test file that references the target
- **When** the run completes
- **Then** no selection warning is emitted
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_mutation.py -k test_no_warning_when_selection_covers_references
- **Verified:** yes (2026-07-20)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-20 | sdlc-studio | Created via `new` (deterministic) |
