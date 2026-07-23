# US0391: critic.py and close_owed.py accept --fields-file via the shared helper

> **Status:** Done
> **Delivers:** CR0392
> **Created:** 2026-07-23
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Epic:** EP0146
> **Points:** 3
> **Affects:** .claude/skills/sdlc-studio/scripts/critic.py,.claude/skills/sdlc-studio/scripts/close_owed.py,.claude/skills/sdlc-studio/scripts/tests/test_critic.py,.claude/skills/sdlc-studio/scripts/tests/test_close_owed.py

## User Story

**As a** agent recording a critic verdict or a close-owed baseline whose prose contains a backtick or a dollar-parenthesis
**I want** critic.py and close_owed.py to accept a `--fields-file` document carrying their free-prose fields, reusing the one helper `file_finding` already exposes
**So that** the prose reaches the artefact as data instead of through a shell that silently empties the field, without either script growing a second bespoke idiom

## Acceptance Criteria

### AC1: critic.py stores fields-file prose exactly as written

- **Given** a `--fields-file` JSON document whose verdict/note prose contains a literal backtick and a dollar-parenthesis
- **When** `critic record ... --fields-file f.json` is run
- **Then** the recorded prose is stored byte-for-byte, backtick and dollar-parenthesis intact, because no value crossed a shell
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic.py::CriticFieldsFileTests::test_fields_file_note_is_stored_verbatim_with_shell_metacharacters
- **Verified:** yes (2026-07-23)

### AC2: close_owed.py stores its baseline note from a fields-file verbatim

- **Given** a `--fields-file` document carrying a baseline note that contains a backtick
- **When** `close_owed baseline --fields-file f.json` is run
- **Then** the note is written to the baseline record byte-for-byte, with the backtick preserved
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_close_owed.py::CloseOwedFieldsFileTests::test_fields_file_baseline_note_is_stored_verbatim
- **Verified:** yes (2026-07-23)

### AC3: both route through the shared loader rather than a second idiom

- **Given** a `--fields-file` document carrying a field name the shared loader does not allow
- **When** either command loads it
- **Then** it is refused with `file_finding.load_fields_file`'s unknown-field error, proving the path goes through the one shared helper and not a re-implemented parser
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic.py::CriticFieldsFileTests::test_unknown_field_is_refused_by_the_shared_loader
- **Verified:** yes (2026-07-23)

## Verification depth

Node-addressed pytest ACs, red before the code. Mutation-proven by hand: dropping the flag-path hazard report and checking the filer's default HAZARD_FIELDS instead of the writer's own keys were each caught. Shell metacharacters (backtick, `$(`) are asserted to survive verbatim because Python never runs them.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-23 | sdlc-studio | Created via `new` (deterministic) |
| 2026-07-23 | sdlc-studio | Built: --fields-file via shared loader + flag-path hazard report, tested, mutation-proven |
