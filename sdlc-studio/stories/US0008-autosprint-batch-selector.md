# US0008: Autosprint batch selector and ordering

> **Status:** Done
> **Epic:** [EP0007: Agentic Orchestration](../epics/EP0007-orchestration.md)
> **Owner:** Autosprint (bootstrap, by hand)
> **Reviewer:** --
> **Created:** 2026-06-20
> **GitHub Issue:** --

## User Story

**As an** autosprint loop
**I want** to select a batch of work by query and order it
**So that** "autosprint --bugs open" / "--crs proposed" yields the triage plan the operator approves before the run (RFC0001 WS2; the batch + order step).

## Context

Implements RFC0001 WS2. Reuses `lib/sdlc_md` (`artifact_files`, `extract_field`, `canonical_status`). Ordering is priority/severity (Critical first); dependency-topological and WSJF (priority over RFC0009 complexity) are layered later.

## Acceptance Criteria

### AC1: Select a type by status

- **Given** bugs with Status `Open` and `Fixed`
- **When** `select_batch(root, "bug", "Open")` runs
- **Then** only the Open bugs are returned, each with id, status, priority, path
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::SelectTests::test_selects_by_status
- **Verified:** yes (2026-07-10)

### AC2: Priority/severity ordering

- **Given** open bugs of Severity Low, Critical, Medium
- **When** the batch is selected with `order="priority"`
- **Then** they are ordered Critical, Medium, Low
- **Verified:** yes (2026-07-10)
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::OrderTests::test_priority_order

### AC3: plan CLI emits an ordered JSON worklist

- **Given** a workspace with proposed CRs
- **When** `autosprint plan --crs Proposed --format json` runs
- **Verified:** yes (2026-07-10)
- **Then** it prints `{ "batch": [...], "count" }` ordered by priority and exits 0
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_sprint.py::CliTests::test_plan_json

## Implementation

`scripts/autosprint.py`: public `select_batch(repo_root, kind, status, order)` + `plan` subcommand (model: `next_id.py`). Priority weight Critical < High < Medium < Low.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-06-20 | Autosprint (bootstrap) | Decomposed from RFC0001 WS2 |
