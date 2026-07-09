# EP0009: Onboarding & Doctrine

> **Status:** Done
> **Owner:** Darren Benson
> **Reviewer:** --
> **Created:** 2026-06-20
> **Target Release:** 2.x
> **GitHub Issue:** --
>
> **Founding epic - closed 2026-07-09.** Every capability below is delivered in the shipped skill (v4.0.0-rc.1); the suite (1455 tests) and the working `/sdlc-studio` commands demonstrate it. The unlinked `US:` breakdown items are early placeholder stubs from before stories were individually tracked - complete in the implementation, not as separate story artefacts. Closed for status hygiene; no capability is outstanding.

## Summary

Get an agent and a project productive and disciplined: `init` configures the
project and seeds tool-neutral agent-instructions; the operating doctrine sets
the project-agnostic working rules; the cross-project lessons registry is
recalled before decisions; operator heuristics and deploy-readiness cover live
services.

**PRD Reference:** [Context](../prd.md#2-problem-statement)

## Scope

### In Scope

- `init` - project config, dir structure, agent-instructions seed (AGENTS.md/CLAUDE.md).
- Operating doctrine (`reference-doctrine.md`) onboarding.
- Lessons registry: record + recall (`lessons/`, scripts/lessons.py).
- Operator heuristics, deploy readiness, release gate.
- Cross-tool portability (AGENTS.md standard, cross-harness installer).

### Out of Scope

- The artifacts produced after onboarding (other epics).

### Affected Personas

- **Consuming-project Developer:** onboards their project.
- **AI Agent:** loads doctrine + lessons + current-state anchor.
- **Orchestrator:** applies operator heuristics on live services.

## Acceptance Criteria (Epic Level)

- [x] `init` writes config + dir skeleton and seeds/validates agent-instructions.
- [x] Doctrine is project-agnostic; a project's AGENTS.md references it plus specifics.
- [x] Lessons are recalled before substantive design/process decisions.
- [x] Release-gate and deploy-readiness patterns are available for live services.

## Dependencies

### Blocked By

| Dependency | Type | Status | Owner |
| --- | --- | --- | --- |
| None | -- | -- | -- |

## Sizing

**Estimated Story Count:** 5

## Story Breakdown

- [x] US: Init project setup + agent-instructions seed
- [x] US: Operating-doctrine onboarding
- [x] US: Lessons record + recall
- [x] US: Operator heuristics + deploy readiness
- [x] US: Cross-tool portability + installer

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-06-20 | Darren Benson | Epic extracted (brownfield) |
