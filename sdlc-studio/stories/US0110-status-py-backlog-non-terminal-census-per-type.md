# US0110: status.py backlog: non-terminal census per type and status (CR0199)

> **Status:** Done
> **Created:** 2026-07-09
> **Created-by:** sdlc-studio new
> **Epic:** EP0025
> **Persona:** Engineering seat
> **Affects:** scripts/status.py, scripts/tests/test_status.py, help/status.md, reference-scripts-review.md

## User Story

**As an** agent asked "what is left in the backlog?"
**I want** a deterministic `status.py backlog` command that lists non-terminal artifacts per type and status from a file census
**So that** the answer is one cheap tool call, not a hand-parsed grep of `_index.md` that misses a `Complete` row

Delivers CR0199.

## Acceptance Criteria

### AC1: backlog lists non-terminal artifacts per type, grouped by status

- **Given** a fixture repo with a mix of terminal and non-terminal artifacts across types
- **When** `status.py backlog` runs
- **Then** it lists only the non-terminal artifacts (CR, story, epic, bug, RFC), grouped by type and status, from a file census
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_status.py::BacklogTests
- **Verified:** yes (2026-07-09)

### AC2: terminal detection is vocabulary-driven, not a hardcoded list

- **Given** a type with several terminal statuses in the shared vocabulary (e.g. a bug's Fixed/Verified/Superseded)
- **When** `backlog` classifies rows
- **Then** it resolves terminal statuses from the shared vocab's full terminal set (via `is_terminal_status`), not a hardcoded Done/Closed subset, so every terminal status is excluded
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_status.py::BacklogVocabTests
- **Verified:** yes (2026-07-09)

### AC3: --format json is stable and --type filters

- **Given** `status.py backlog`
- **When** invoked with `--format json` and with `--type cr`
- **Then** it emits a stable JSON structure, and `--type cr` restricts the output to change requests
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_status.py::BacklogFormatTests
- **Verified:** yes (2026-07-09)

### AC4: an empty backlog prints explicitly, and the command is documented

- **Given** a repo with no non-terminal artifacts
- **When** `backlog` runs, and when the docs are read
- **Then** it states the backlog is empty (not blank output), and `help/status.md` + the scripts reference document the command
- **Verify:** grep "backlog" .claude/skills/sdlc-studio/help/status.md
- **Verified:** yes (2026-07-09)

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-07-09 | sdlc | Created via `new` (deterministic) |
| 2026-07-09 | claude | Groomed from CR0199 (deterministic backlog census) |
