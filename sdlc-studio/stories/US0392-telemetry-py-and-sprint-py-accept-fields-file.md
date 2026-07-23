# US0392: telemetry.py and sprint.py accept --fields-file and the registry is emptied of the four

> **Status:** Draft
> **Delivers:** CR0392
> **Created:** 2026-07-23
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Epic:** EP0146
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/telemetry.py,.claude/skills/sdlc-studio/scripts/sprint.py,.claude/skills/sdlc-studio/scripts/tests/test_telemetry.py,.claude/skills/sdlc-studio/scripts/tests/test_sprint.py,.claude/skills/sdlc-studio/scripts/tests/test_artifact.py

## User Story

**As a** agent recording a telemetry outcome or planning a sprint with prose that contains shell metacharacters
**I want** telemetry.py and sprint.py to accept `--fields-file` via the shared loader, and the four converted writers removed from `KNOWN_PROSE_WRITER_GAPS`
**So that** all four siblings share the safe path and the debt registry no longer records a gap that has already been paid

## Acceptance Criteria

### AC1: telemetry.py stores fields-file prose verbatim

- **Given** a `--fields-file` document whose summary/verdict/note prose contains a backtick and a dollar-parenthesis
- **When** `telemetry record --fields-file f.json` is run
- **Then** the prose is stored on the record byte-for-byte, because it did not cross a shell
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_telemetry.py::TelemetryFieldsFileTests::test_fields_file_prose_is_stored_verbatim

### AC2: sprint.py consumes goal and note prose from a fields-file verbatim

- **Given** a `--fields-file` document carrying a sprint goal and note that contain a backtick
- **When** the sprint command consumes it via `--fields-file`
- **Then** both fields are stored byte-for-byte with the backtick preserved
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::SprintFieldsFileTests::test_fields_file_goal_and_note_are_stored_verbatim

### AC3: the registry is emptied of the four converted writers

- **Given** critic.py, close_owed.py, telemetry.py and sprint.py now offer `--fields-file`
- **When** the prose-writer sweep runs
- **Then** all four appear in `SAFE_INPUT_WRITERS` and none remains in `KNOWN_PROSE_WRITER_GAPS`, leaving only the recorded mutation.py exception
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_artifact.py::ProseWriterSweepTests::test_the_four_cr0392_writers_are_now_safe

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-23 | sdlc-studio | Created via `new` (deterministic) |
