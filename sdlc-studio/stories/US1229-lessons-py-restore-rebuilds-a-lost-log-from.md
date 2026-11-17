# US1229: lessons.py restore rebuilds a lost log from the digest and refuses to overwrite an existing log

> **Status:** Draft
> **Risk-class:** standard
> **Delivers:** CR0688
> **Created:** 2026-11-17
> **Created-by:** sdlc-studio new
> **Raised-by:** sdlc-studio; agent; v1
> **Affects:** .claude/skills/sdlc-studio/scripts/lessons.py, .claude/skills/sdlc-studio/scripts/tests/test_lessons_restore.py, .claude/skills/sdlc-studio/help/lessons.md
> **Epic:** EP0337
> **Points:** 3
> **Persona:** Abena Osei

## User Story

**As a** Abena Osei
**I want** lessons.py restore rebuilds a lost log from the digest and refuses to overwrite an existing log
**So that** CR0688 is delivered by work that can be planned and checked

## Acceptance Criteria

### AC1: Restore rebuilds the log so the digest guard passes

- **Given** a project with a committed LESSONS-SUMMARY.md listing several lessons and no lessons log, neither the committed one nor the legacy local one
- **When** `lessons.py restore --from-summary` is run, then `lessons.py summary`
- **Then** the log holds one lesson for each digest item under its own id and title, each body saying it was reconstructed from the digest and what was lost (the body, the dates and any text past the digest's cut), and `summary` regenerates a digest that keeps every lesson instead of refusing. Fails on: an id renumbered, a title changed, or a body that reads as the original lesson
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lessons_restore.py::LessonsRestoreTests::test_restore_rebuilds_each_digest_item_and_the_summary_guard_passes

### AC2: Restore refuses when a log already exists

- **Given** a project whose lessons log exists, with one lesson the digest does not list
- **When** `lessons.py restore --from-summary` is run
- **Then** it exits non-zero saying a log already exists, and the log's bytes are unchanged. Fails on: an existing log overwritten or merged with reconstructed entries
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lessons_restore.py::LessonsRestoreTests::test_restore_refuses_to_overwrite_an_existing_log

### AC3: The summary refusal and the help name restore as the remedy

- **Given** the project with a digest and no log
- **When** `lessons.py summary` is run
- **Then** its refusal names `lessons.py restore --from-summary` as the remedy when no machine holds the log, and `help/lessons.md` documents the command and what a restored lesson lacks. Fails on: a refusal that still offers only the machine that ran the last close
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_lessons_restore.py::LessonsRestoreTests::test_the_summary_refusal_and_the_help_name_restore

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-11-17 | sdlc-studio | Created via `new` (deterministic) |
