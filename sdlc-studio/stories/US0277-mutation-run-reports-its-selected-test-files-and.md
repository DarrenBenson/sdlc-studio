# US0277: Mutation run reports its selected test files and records the test command in the JSON result

> **Status:** Draft
> **Delivers:** CR0363
> **Created:** 2026-07-20
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/mutation.py, .claude/skills/sdlc-studio/help/mutation.md
> **Epic:** EP0091
> **Depends on:** BG0215
> **Points:** 2

## User Story

**As a** consumer of the mutation gate
**I want** every run to show what its test command actually selected
**So that** a survivor is never read without knowing what was run against it

## Acceptance Criteria

### AC1: the run reports the test files its command selects

- **Given** a mutation run over a target module with a test command
- **When** the run completes
- **Then** the report lists the test files the command selected, beside the survivor list, so a
  reader can see what the survivors were measured against
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_mutation.py -k test_report_lists_selected_test_files

### AC2: the test command is recorded in the JSON result

- **Given** the run writes its JSON output
- **When** a result is recorded
- **Then** the JSON carries the test command beside the survivors, so a survivor read later
  cannot be separated from the command that produced it
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_mutation.py -k test_json_records_test_command

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-20 | sdlc-studio | Created via `new` (deterministic) |
