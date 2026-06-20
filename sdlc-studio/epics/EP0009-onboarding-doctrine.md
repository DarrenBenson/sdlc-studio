# EP0009: Onboarding & Doctrine

> **Status:** Ready
> **Owner:** Darren Benson
> **Reviewer:** --
> **Created:** 2026-06-20
> **Target Release:** 2.x
> **GitHub Issue:** --

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

- [ ] `init` writes config + dir skeleton and seeds/validates agent-instructions.
- [ ] Doctrine is project-agnostic; a project's AGENTS.md references it plus specifics.
- [ ] Lessons are recalled before substantive design/process decisions.
- [ ] Release-gate and deploy-readiness patterns are available for live services.

## Dependencies

### Blocked By

| Dependency | Type | Status | Owner |
| --- | --- | --- | --- |
| None | -- | -- | -- |

## Sizing

**Estimated Story Count:** 5

## Story Breakdown

- [ ] US: Init project setup + agent-instructions seed
- [ ] US: Operating-doctrine onboarding
- [ ] US: Lessons record + recall
- [ ] US: Operator heuristics + deploy readiness
- [ ] US: Cross-tool portability + installer

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-06-20 | Darren Benson | Epic extracted (brownfield) |
