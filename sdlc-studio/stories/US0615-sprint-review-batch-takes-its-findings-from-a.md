# US0615: sprint review-batch takes its findings from a fields-file, so prose carrying backticks is stored verbatim rather than executed

> **Status:** Done
> **Closed with findings in:** repaired in 307ce91d - the verifier drives review-batch --fields-file
> **Delivers:** CR0516
> **Created:** 2026-08-01
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/sprint.py, .claude/skills/sdlc-studio/scripts/tests/test_sprint.py
> **Epic:** EP0203
> **Points:** 3

## User Story

**As a** reviewer recording findings that contain shell metacharacters
**I want** review-batch findings read from a fields-file
**So that** prose carrying backticks is stored verbatim rather than executed by the shell

## Acceptance Criteria

### AC1: review-batch takes findings from a fields-file

- **Given** findings text containing backticks and `$(`
- **When** it is passed via `--fields-file`
- **Then** it is stored verbatim, because on the flag path that prose is command substitution
- **Verify:** manual - retired by US0918: `sprint.py review-batch` and its `--fields-file` are retired
- **Verified:** manual (2026-09-26) - retired, superseded by US0918

### AC2: the flag path still works

- **Given** ordinary findings text with no metacharacters
- **When** it is passed via `--findings`
- **Then** it records as before, so the fields-file is an addition rather than a migration
- **Verify:** manual - retired by US0918: `sprint.py review-batch` and its `--fields-file` are retired
- **Verified:** manual (2026-09-26) - retired, superseded by US0918

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-08-01 | sdlc-studio | Created via `new` (deterministic) |
| 2026-09-26 | US0918 | AC1 and AC2 retired in the D0259 pattern: `sprint.py review-batch` and its `--fields-file` are retired |
