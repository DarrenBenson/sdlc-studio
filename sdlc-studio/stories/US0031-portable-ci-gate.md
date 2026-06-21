# US0031: portable CI quality gate

> **Status:** Done
> **Epic:** [EP0008: Tooling & Scripts](../epics/EP0008-tooling-scripts.md)
> **Owner:** Autosprint (CR0046)
> **Reviewer:** --
> **Created:** 2026-06-21
> **GitHub Issue:** --

## User Story

**As a** team adopting SDLC Studio in any CI
**I want** one command that runs the deterministic checks and fails the build on drift
**So that** the discipline is enforced on every change, not just available (CR0046).

## Acceptance Criteria

### AC1: Aggregates the checks with correct blocking semantics

- **Given** a set of checks
- **When** `run_gate` runs them
- **Then** it reports each check's pass/fail, and `ok` is False only when a *blocking* check fails (a non-blocking failure is reported but does not fail the gate)
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_gate.py::GateLogicTests
- **Verified:** yes (2026-06-21)

### AC2: `--only` / `--skip` select checks; empty selection is OK

- **Given** the check registry
- **When** `--only` / `--skip` are applied
- **Then** only the intended checks run, and an empty selection passes
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_gate.py::GateLogicTests::test_only_selects_subset
- **Verified:** yes (2026-06-21)

### AC3: The five real checks run end-to-end (drift counted correctly)

- **Given** this repo
- **When** the real wrappers run
- **Then** all five checks execute and return well-formed results, and reconcile counts drift items (not dict keys)
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_gate.py::GateRealWrapperTests
- **Verified:** yes (2026-06-21)

## Implementation

`scripts/gate.py` (`run_gate` + injectable registry + 5 real check wrappers + CLI, exit 1
on blocking failure, no network); `help/gate.md` (command + GitHub Actions / GitLab /
shell-pre-commit wiring); SKILL.md + reference-scripts.md rows.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-06-21 | Autosprint (CR0046) | Decomposed from CR0046; critic fixed the reconcile dict-vs-list count before APPROVE |
