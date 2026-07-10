# US0016: epic implement --resume

> **Status:** Done
> **Epic:** [EP0007: Agentic Orchestration](../epics/EP0007-orchestration.md)
> **Owner:** Autosprint (CR0007, determinism-sprint)
> **Reviewer:** --
> **Created:** 2026-06-20
> **GitHub Issue:** --

## User Story

**As an** operator
**I want** `epic implement --resume` to restart at the first non-Done story
**So that** a mid-batch failure recovers deterministically instead of re-running
Done stories or a manual `--story` restart (CR0007).

## Context

Implements CR0007. `scripts/resume.py` computes the resume point from each story's
canonical **Status** (the authoritative Done signal, not a drift-prone workflow
table - the CR0004 lesson) and persists run-state to `.local/epic-state.json`,
mirroring `project implement --resume`. Wired into `reference-epic.md`.

## Acceptance Criteria

### AC1: Resume at the first non-Done story

- **Given** an epic whose stories are Done, Done, Ready, Ready
- **When** `resume_point(root, epic)` runs
- **Then** it returns the first non-Done story; all-Done returns None
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_resume.py::ResumePointTests
- **Verified:** yes (2026-06-20)

### AC2: Only the target epic's stories count

- **Given** stories under two epics
- **When** the resume point for one epic is computed
- **Then** only that epic's stories are considered (resolved via the Epic link)
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_resume.py::ResumePointTests::test_only_target_epic_counted
- **Verified:** yes (2026-06-20)

### AC3: Run-state persisted to .local

- **Given** a partially-done epic
- **When** `write_state` runs
- **Then** `.local/epic-state.json` records `resume_at`, the ordered stories, and `complete`
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_resume.py::StateTests::test_write_state_persists
- **Verified:** yes (2026-06-20)

### AC4: Documented in the epic reference

- **Given** `reference-epic.md`
- **When** searched
- **Then** `epic implement --resume` is documented
- **Verify:** grep "epic implement --resume" .claude/skills/sdlc-studio/reference-epic.md
- **Verified:** yes (2026-07-10)

## Implementation

`scripts/resume.py`: `epic_stories`, `resume_point`, `build_state`, `write_state`
plus a `resume` CLI. Doc in `reference-epic.md#epic-implement-resume`.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-06-20 | Autosprint (CR0007) | Decomposed from CR0007 (determinism sprint) |
