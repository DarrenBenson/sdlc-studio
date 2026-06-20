# US0010: Deterministic loop guardrails

> **Status:** Ready
> **Epic:** [EP0007: Agentic Orchestration](../epics/EP0007-orchestration.md)
> **Owner:** Autosprint (CR0020, by hand)
> **Reviewer:** --
> **Created:** 2026-06-20
> **GitHub Issue:** --

## User Story

**As an** autosprint loop
**I want** deterministic cap, repetition-breaker and completion checks
**So that** I cannot thrash a unit forever, cannot silently drop one, and cannot
declare the batch done while units are unfinished (RFC0001 D5/D2, WS3).

## Context

Implements RFC0001 WS3. The three judgements the model must not own: am-I-stuck
(cap + repetition-breaker), am-I-done (completion oracle). Pure functions over a
state dict so they are trivially testable; the CLI persists state to
`sdlc-studio/.local/loop-state.json` (run-local, like `project-state.json`).
Quarantine = mark the unit Blocked and continue (D2), never thrash, never drop.

## Acceptance Criteria

### AC1: Iteration cap quarantines

- **Given** a unit with `cap=3`
- **When** a 3rd failed attempt is recorded
- **Then** `verdict` reports `quarantine=True` with reason `cap`
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_loop_guard.py::CapTests::test_cap_quarantines
- **Verified:** pending

### AC2: Repetition-breaker quarantines early

- **Given** a unit under the cap but the same failure signature seen `repeat=2` times
- **When** `verdict` runs
- **Then** it reports `quarantine=True` with reason `repeat`
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_loop_guard.py::RepeatTests::test_repeat_quarantines
- **Verified:** pending

### AC3: Completion oracle

- **Given** unit statuses `["Done", "Blocked", "Done"]`
- **When** `is_complete` runs
- **Then** it returns True (all terminal); `["Done", "In Progress"]` returns False
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_loop_guard.py::CompleteTests::test_all_terminal
- **Verified:** pending

### AC4: CLI record persists and signals quarantine

- **Given** a temp state file
- **When** `loop_guard.py record --unit US --signature s --cap 1 --state <path>` runs
- **Then** it exits 3 (quarantine signal) and the state file records the attempt
- **Verify:** pytest .claude/skills/sdlc-studio/scripts/tests/test_loop_guard.py::CliTests::test_record_quarantine_exit
- **Verified:** pending

## Implementation

`scripts/loop_guard.py`: pure `record_attempt(state, unit, signature)`,
`verdict(state, unit, cap, repeat)`, `is_complete(statuses)`; `record`/`status`
subcommands persisting `loop-state.json`. Exit 3 on quarantine.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-06-20 | Autosprint (CR0020) | Decomposed from CR0020 / RFC0001 WS3 |
