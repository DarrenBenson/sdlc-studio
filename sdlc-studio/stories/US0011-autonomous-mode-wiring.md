# US0011: Autonomous mode wiring

> **Status:** Ready
> **Epic:** [EP0007: Agentic Orchestration](../epics/EP0007-orchestration.md)
> **Owner:** Autosprint (CR0020, by hand)
> **Reviewer:** --
> **Created:** 2026-06-20
> **GitHub Issue:** --

## User Story

**As an** operator
**I want** the `--autonomous` mode documented end to end
**So that** an unattended autosprint ties the ledger, the guardrails, the
independent critic and the closing gate into one understood policy (RFC0001
WS6/WS4).

## Context

Implements RFC0001 WS6 (and documents WS4, the independent non-author critic, as a
model-instructed loop step). A documentation unit: the deterministic enforcement
lives in US0009 (ledger) and US0010 (guardrails); this story wires them into the
narrated `--autonomous` policy across the reference docs and help. AC are verified
by content checks (`rg`), the skill's supported doc-verifier style.

## Acceptance Criteria

### AC1: Autonomous mode documented in the autosprint reference

- **Given** `reference-autosprint.md`
- **When** searched for the autonomous-mode policy
- **Then** it describes `--autonomous`, the ledger, the cap/repetition/completion guardrails, quarantine-and-continue, and the closing reconcile + review
- **Verify:** rg -q "autonomous" .claude/skills/sdlc-studio/reference-autosprint.md
- **Verified:** pending

### AC2: Independent critic recorded as a loop step

- **Given** `reference-autosprint.md`
- **When** searched for the critic step
- **Then** the non-author critic (D3/WS4) is present in the per-unit loop
- **Verify:** rg -q "critic" .claude/skills/sdlc-studio/reference-autosprint.md
- **Verified:** pending

### AC3: project implement notes the autonomous mode

- **Given** `reference-project.md`
- **When** searched
- **Then** it cross-references `--autonomous` / autosprint as the outer loop over the wave engine
- **Verify:** rg -q "autonomous" .claude/skills/sdlc-studio/reference-project.md
- **Verified:** pending

### AC4: help documents the flag

- **Given** `help/autosprint.md`
- **When** searched
- **Then** the `--autonomous` flag is documented
- **Verify:** rg -q "autonomous" .claude/skills/sdlc-studio/help/autosprint.md
- **Verified:** pending

## Implementation

Doc edits to `reference-autosprint.md`, `reference-project.md`, `help/autosprint.md`
tying ledger + guardrails + critic + closing gate into the `--autonomous` policy.

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-06-20 | Autosprint (CR0020) | Decomposed from CR0020 / RFC0001 WS6 |
