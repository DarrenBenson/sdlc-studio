# US0390: the batch-selection message shows a usable example value per selector, such as --bugs Open

> **Status:** Draft
> **Delivers:** CR0390
> **Created:** 2026-07-23
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Epic:** EP0145
> **Points:** 1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_batch_selection.py

## User Story

**As a** agent or operator invoking sprint plan on the hottest path in the skill
**I want** the batch-selection error to show a usable example value per selector
**So that** the first retry after it is a working invocation rather than two more failed round-trips

## Acceptance Criteria

### AC1: the message shows a usable example value per selector

- **Given** `sprint plan` invoked with no batch selected
- **When** the batch-selection error prints
- **Then** each status-taking selector appears with an example status value (such as `--bugs Open`), so copying the suggestion yields a working invocation
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_batch_selection.py::BatchSelectionError::test_message_shows_example_status_per_selector

### AC2: a valid status value is discoverable from the failure itself

- **Given** the same no-batch invocation
- **When** the batch-selection error prints
- **Then** a valid status value is present in the message text, so it is discoverable from the failure rather than only from the help file
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_batch_selection.py::BatchSelectionError::test_valid_status_value_present_in_message

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-23 | sdlc-studio | Created via `new` (deterministic) |
