# US0019: verify_ac report history and dry-run record

> **Status:** Done
> **Epic:** [EP0005: Quality & Drift Control](../epics/EP0005-quality-drift.md)
> **Owner:** Autosprint (CR0005, backlog-closeout)
> **Reviewer:** --
> **Created:** 2026-06-20
> **GitHub Issue:** --

## User Story

**As an** operator
**I want** the dry-run to persist which ACs would flip, and every run logged
**So that** the safe preview is recoverable and the gate has an audit trail
("when did AC-3 last pass?") instead of a single overwriting snapshot (CR0005).

## Context

Implements CR0005. `verify_story` records per-AC `flips` (ac, old_state,
new_state); `write_report` writes in dry-run too (to a distinct `.dry-run.json`
path, with a `dry_run` flag and the flips); `append_history` appends one JSONL
line per story per run to `.local/verify-history.jsonl`.

## Acceptance Criteria

### AC1: Dry-run enumerates pending flips and touches nothing

- **Given** a story with an AC that would flip to Verified
- **When** `verify_story(dry_run=True)` runs
- **Then** the report's `flips` list carries `(ac, old_state, new_state)` and the story file is unchanged
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_verify_ac.py::ReportHistoryTests::test_dry_run_records_flips_without_modifying_file
- **Verified:** yes (2026-06-20)

### AC2: Report carries the dry_run flag and flips

- **Given** a dry-run report
- **When** `write_report(..., dry_run=True)` runs
- **Then** the JSON has `dry_run: true` and the story's `flips`
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_verify_ac.py::ReportHistoryTests::test_write_report_has_flips_and_dry_run_flag
- **Verified:** yes (2026-06-20)

### AC3: Each run appends to the history log

- **Given** two runs
- **When** `append_history` runs each time
- **Then** `.local/verify-history.jsonl` has one line per story per run (append-only)
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_verify_ac.py::ReportHistoryTests::test_history_is_append_only
- **Verified:** yes (2026-06-20)

## Implementation

`scripts/verify_ac.py`: `StoryReport.flips`; `write_report(dry_run=)`;
`append_history`; `cmd_run` writes a `.dry-run.json` and appends history every run.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-06-20 | Autosprint (CR0005) | Decomposed from CR0005 (backlog-closeout) |
