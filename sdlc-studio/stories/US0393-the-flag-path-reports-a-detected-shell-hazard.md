# US0393: the flag path reports a detected shell hazard rather than silently altering the field

> **Status:** Done
> **Delivers:** CR0392
> **Created:** 2026-07-23
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Epic:** EP0146
> **Points:** 2
> **Affects:** .claude/skills/sdlc-studio/scripts/critic.py,.claude/skills/sdlc-studio/scripts/close_owed.py,.claude/skills/sdlc-studio/scripts/telemetry.py,.claude/skills/sdlc-studio/scripts/sprint.py,.claude/skills/sdlc-studio/scripts/tests/test_prose_writer_hazard.py

## User Story

**As a** operator passing prose on the legacy flag path rather than through `--fields-file`
**I want** each of the four commands to detect and report a shell hazard in a flag value rather than silently storing an altered field
**So that** a fails-open truncation becomes a visible warning that points me at `--fields-file`, while the flag path still works for compatibility

## Acceptance Criteria

### AC1: the flag path reports a detected shell hazard on stderr

- **Given** the legacy flag path receives prose bearing the marks a shell already ate it (an unbalanced backtick, or a surviving dollar-parenthesis)
- **When** any of critic.py, close_owed.py, telemetry.py or sprint.py is run that way
- **Then** it emits `file_finding.report_shell_hazards`' warning on stderr naming the affected field, rather than storing the altered value silently
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_prose_writer_hazard.py::FlagPathHazardTests::test_each_writer_reports_a_hazard_on_stderr
- **Verified:** yes (2026-07-23)

### AC2: the warning does not block the flag path

- **Given** a hazardous value on the flag path that triggers the hazard warning
- **When** the command runs
- **Then** in the same run the warning is emitted AND the command exits 0 AND the field is written, so the report coexists with the write rather than becoming a new refusal that breaks existing callers
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_prose_writer_hazard.py::FlagPathHazardTests::test_the_warning_is_emitted_yet_does_not_block_the_flag_path
- **Verified:** yes (2026-07-23)

### AC3: the fields-file path raises no hazard warning

- **Given** the same prose supplied through `--fields-file`
- **When** the command runs
- **Then** no shell-hazard warning is emitted, because the value never crossed a shell to be altered
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_prose_writer_hazard.py::FlagPathHazardTests::test_fields_file_prose_raises_no_hazard_warning
- **Verified:** yes (2026-07-23)

## Verification depth

Node-addressed pytest ACs, red before the code. Mutation-proven by hand: dropping the flag-path hazard report and checking the filer's default HAZARD_FIELDS instead of the writer's own keys were each caught. Shell metacharacters (backtick, `$(`) are asserted to survive verbatim because Python never runs them.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-23 | sdlc-studio | Created via `new` (deterministic) |
| 2026-07-23 | sdlc-studio | Built: --fields-file via shared loader + flag-path hazard report, tested, mutation-proven |
