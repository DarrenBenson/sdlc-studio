# US0406: goal-review record accepts a --fields-file so no seat prose crosses a shell

> **Status:** Review
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py
> **Delivers:** CR0409
> **Created:** 2026-07-23
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Epic:** EP0153
> **Points:** 2

## User Story

**As a** reviewer recording a seat verdict that quotes commands and paths
**I want** to pass the verdict through a --fields-file rather than a shell argument
**So that** a note containing backticks is stored as written instead of being executed or silently deleted

## Acceptance Criteria

### AC1: record reads seat verdicts from a fields file

- **Given** a fields-file document holding a seat's verdict
- **When** `goal-review record` is run with --fields-file and no --seat argument
- **Then** the seats are recorded from the file
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::GoalReviewFieldsFileTests::test_record_reads_seat_verdicts_from_a_fields_file

### AC2: a note with shell metacharacters is stored verbatim

- **Given** a seat note quoting a command in backticks, the measured CR0409 case where a word was silently deleted
- **When** the verdict is recorded through the fields file
- **Then** the note is stored byte-for-byte, with no word deleted and no command substitution performed
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::GoalReviewFieldsFileTests::test_a_note_with_backticks_is_stored_verbatim

## Verification depth

Node-addressed pytest ACs over `test_sprint.py`, red before the code. Mutation-proven by hand: dropping the amendment carry-forward, letting a material change carry, inverting the needs-reconsult set, not storing the brief in the round, and ignoring the fields-file seats were each caught by a node.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-23 | sdlc-studio | Created via `new` (deterministic) |
| 2026-07-23 | sdlc-studio | Built and mutation-proven |
