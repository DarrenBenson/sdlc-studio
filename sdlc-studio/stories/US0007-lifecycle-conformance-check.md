# US0007: Lifecycle-conformance check

> **Status:** Done
> **Epic:** [EP0007: Agentic Orchestration](../epics/EP0007-orchestration.md)
> **Owner:** Autosprint (bootstrap, by hand)
> **Reviewer:** --
> **Created:** 2026-06-20
> **GitHub Issue:** --

## User Story

**As an** autosprint loop
**I want** a deterministic check that a unit passed through the required lifecycle stages
**So that** "everything was used" is enforced (the fourth guardrail, RFC0001 WS7), not trusted - a unit cannot reach Done with a stage silently skipped.

## Context

Implements RFC0001 WS7. Aggregates signals already produced by the skill (epic link, AC, Verify line, Verified state) into a per-unit pass/fail, hard-failing on any gap. Reconciled/reviewed signals are layered in later; v1 covers the structural core.

## Acceptance Criteria

### AC1: Per-story stage flags

- **Given** a story with an Epic link, at least one AC, and at least one `Verify:` line
- **When** `detect_conformance(root)` runs
- **Then** that story's `stages` show `decomposed`, `specified`, `verifiable` all true
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_conformance.py::StageTests::test_full_story_all_stages_true
- **Verified:** yes (2026-06-20)

### AC2: A missing required stage is flagged

- **Given** a story with no Epic link (or no AC, or no `Verify:` line)
- **When** the check runs
- **Then** the story is non-conformant and `missing` lists the absent stage
- **Verified:** yes (2026-06-20)
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_conformance.py::StageTests::test_missing_stage_flagged

### AC3: Done stories must be verified

- **Given** a story with Status `Done` whose AC are not all `Verified: yes`
- **When** the check runs
- **Verified:** yes (2026-06-20)
- **Then** the story is non-conformant with `verified` in `missing`
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_conformance.py::StageTests::test_done_must_be_verified

### AC4: Exit code and JSON shape

- **Given** any non-conformant in-scope unit
- **Verified:** yes (2026-06-20)
- **When** `conformance` runs as a CLI
- **Then** it exits non-zero (0 when all conform), and emits `{ "units": [ { "id", "conformant", "missing" } ], "summary": { "total", "conformant", "nonconformant" } }`
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_conformance.py::CliTests::test_exit_and_shape

## Implementation

`scripts/conformance.py`: public `detect_conformance(repo_root)` + `conformance` subcommand (model: `next_id.py collisions`). Reuses `lib/sdlc_md` (`artifact_files`, `extract_field`, `canonical_status`, `AC_*`/`VERIFY_RE`/`VERIFIED_RE`).

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-06-20 | Autosprint (bootstrap) | Decomposed from RFC0001 WS7 |
