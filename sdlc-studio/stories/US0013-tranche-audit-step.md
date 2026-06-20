# US0013: Tranche-audit step

> **Status:** Done
> **Epic:** [EP0007: Agentic Orchestration](../epics/EP0007-orchestration.md)
> **Owner:** Autosprint (CR0021, determinism-sprint)
> **Reviewer:** --
> **Created:** 2026-06-20
> **GitHub Issue:** --

## User Story

**As an** autosprint loop
**I want** a pre-flight tranche audit before the triage STOP
**So that** the operator approves a clean, verifiable batch instead of one with
tautological AC, unmet deps, or already-done items (CR0021).

## Context

Implements CR0021. New `scripts/audit.py` (weak-AC, unmet-deps, already-terminal,
reusing `integrity.py` for link-integrity) emits a JSON readiness report; non-zero
exit when any unit is not ready. The workflow step is documented in
`reference-autosprint.md` between `plan` and the triage STOP. Adversarial "is the
problem still real" stays model-instructed (delegates to RFC0002 when built).

## Acceptance Criteria

### AC1: Weak-AC detection

- **Given** a CR whose only AC is the tautology placeholder, and a CR with concrete AC
- **When** `audit_unit` runs on each
- **Then** the first is not ready (issue `weak-AC`) and the second is ready
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_audit.py::WeakAcTests::test_tautology_is_weak
- **Verified:** yes (2026-06-20)

### AC2: Unmet-deps and already-terminal

- **Given** a CR depending on an unfinished CR, and an already-Complete CR
- **When** the audit runs
- **Then** the first flags `unmet-deps` and the second flags `already-terminal`
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_audit.py::DepsTerminalTests::test_already_terminal
- **Verified:** yes (2026-06-20)

### AC3: JSON readiness report + non-zero exit

- **Given** a batch with one ready and one not-ready unit
- **When** `audit.py check --ids ... --format json` runs
- **Then** it prints a `summary` and exits non-zero (a unit is not ready)
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_audit.py::CliTests::test_batch_json_and_exit
- **Verified:** yes (2026-06-20)

### AC4: Workflow step documented

- **Given** `reference-autosprint.md`
- **When** searched for the tranche-audit step
- **Then** step 2 "Tranche audit" sits between `plan` and the triage STOP
- **Verify:** rg -q "Tranche audit" .claude/skills/sdlc-studio/reference-autosprint.md
- **Verified:** yes (2026-06-20)

## Implementation

`scripts/audit.py`: `audit_unit` / `audit_batch` plus a `check` subcommand; reuses
`integrity.py` and `autosprint.select_batch`. Doc step in `reference-autosprint.md`
and `help/autosprint.md`.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-06-20 | Autosprint (CR0021) | Decomposed from CR0021 (determinism sprint) |
