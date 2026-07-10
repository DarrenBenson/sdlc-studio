# US0017: Conformance gate completion

> **Status:** Done
> **Epic:** [EP0007: Agentic Orchestration](../epics/EP0007-orchestration.md)
> **Owner:** Autosprint (CR0023, tooling-honesty-sprint)
> **Reviewer:** --
> **Created:** 2026-06-20
> **GitHub Issue:** --

## User Story

**As an** operator
**I want** the conformance gate to verify reconciled + a recorded critic verdict
**So that** "conformant" means the full lifecycle ran - including the independent
critic, which previously left no gated trace (CR0023).

## Context

Implements CR0023. New `scripts/critic.py` records the independent-critic verdict
(RFC0001 D3) to a committed `sdlc-studio/reviews/critic-verdicts.md`. `conformance.py`
gains two required stages for Done stories: **reconciled** (no index drift, reusing
`reconcile.detect_type`) and **critiqued** (a committed APPROVE). Pre-existing Done
stories were backfilled. The batch-level "reviewed" remains the closing gate.

## Acceptance Criteria

### AC1: Committed critic-verdict record

- **Given** a unit
- **When** `critic.record_verdict(root, unit, "approve")` runs and another verdict is later appended
- **Then** the record is append-only and `verdict_for` returns the latest verdict
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_critic.py::RecordTests
- **Verified:** yes (2026-06-20)

### AC2: Done requires a critic APPROVE (critiqued stage)

- **Given** a Done story
- **When** it has no verdict / a REJECT / an APPROVE
- **Then** conformance flags `critiqued` missing for the first two and conformant for APPROVE
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_conformance.py::CritiqueStageTests
- **Verified:** yes (2026-06-20)

### AC3: Done requires no index drift (reconciled stage)

- **Given** a Done story whose index status mismatches its file
- **When** conformance runs
- **Then** the `reconciled` stage is missing (non-conformant)
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_conformance.py::ReconciledStageTests::test_done_with_index_drift_not_reconciled
- **Verified:** yes (2026-06-20)

## Implementation

`scripts/critic.py`: `record_verdict`/`verdict_for`/`read_verdicts` + `record`/`show`
CLI. `conformance.py`: `reconciled` + `critiqued` required stages for Done; docs
updated in `reference-sprint.md`.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-06-20 | Autosprint (CR0023) | Decomposed from CR0023 (tooling-honesty sprint) |
