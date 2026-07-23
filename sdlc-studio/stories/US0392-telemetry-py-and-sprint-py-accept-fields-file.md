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

### AC1: telemetry.py is confirmed safe-by-nature (it takes no free prose)

**Corrected during delivery.** The grooming premise (inherited from the `KNOWN_PROSE_WRITER_GAPS`
comment "note prose on the command line") was WRONG: telemetry.py has no narrative flag. Its only
`_PROSE_FLAGS` match is `show --summary`, a `store_true` BOOLEAN, so there is no prose to store and
no shell hazard. It is reclassified safe-by-nature (like mutation.py), not given a `--fields-file`
for prose that does not exist.

- **Given** the prose-writer sweep enumerates telemetry.py
- **When** its `KNOWN_PROSE_WRITER_GAPS` entry is read
- **Then** telemetry is recorded as safe-by-nature (a boolean flag, no free prose), not a deferred gap
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_artifact.py::ProseWriterSweepTests::test_the_four_cr0392_writers_are_now_safe

### AC2: sprint.py consumes goal and note prose from a fields-file verbatim

- **Given** a `--fields-file` document carrying a sprint goal and note that contain a backtick
- **When** the sprint command consumes it via `--fields-file`
- **Then** both fields are stored byte-for-byte with the backtick preserved
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::SprintFieldsFileTests::test_fields_file_goal_and_note_are_stored_verbatim

### AC3: the registry no longer defers any of the four writers

- **Given** critic.py, close_owed.py and sprint.py now offer `--fields-file`, and telemetry.py is confirmed safe-by-nature
- **When** the prose-writer sweep runs
- **Then** the three prose writers appear in `SAFE_INPUT_WRITERS`, telemetry remains a named safe-by-nature gap, and none of the four is recorded as a `deferred` gap (leaving only the mutation.py exception beside telemetry)
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_artifact.py::ProseWriterSweepTests::test_the_four_cr0392_writers_are_now_safe

## Verification depth

Node-addressed pytest ACs, red before the code. Mutation-proven by hand: dropping the flag-path hazard report and checking the filer's default HAZARD_FIELDS instead of the writer's own keys were each caught. Shell metacharacters (backtick, `$(`) are asserted to survive verbatim because Python never runs them.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-23 | sdlc-studio | Created via `new` (deterministic) |
| 2026-07-23 | sdlc-studio | Built: --fields-file via shared loader + flag-path hazard report, tested, mutation-proven |
