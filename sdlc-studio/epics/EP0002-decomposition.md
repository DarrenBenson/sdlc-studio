# EP0002: Decomposition (Epics & Stories)

> **Status:** Ready
> **Owner:** Darren Benson
> **Reviewer:** --
> **Created:** 2026-06-20
> **Target Release:** 2.x
> **GitHub Issue:** --

## Summary

Decompose requirements into epics and then into user stories with
implementation-ready acceptance criteria. Includes `story generate` - the
reverse-engineering path that extracts real validation rules, error messages and
API contracts from code rather than from epic descriptions.

**PRD Reference:** [Feature Inventory](../prd.md#3-feature-inventory)

## Scope

### In Scope

- Epic decomposition from PRD, with engineering/product/test perspectives.
- Story creation from epic AC, and `story generate` from code.
- Story Ready criteria + quality checklist enforcement.

### Out of Scope

- Implementation planning (EP0003).
- Completion cascades and drift fixes (EP0005).

### Affected Personas

- **Orchestrator:** decomposes the backlog.
- **AI Agent:** consumes story AC as the unit of work.

## Acceptance Criteria (Epic Level)

- [ ] Epics map back to PRD features via the Feature Inventory Epic column.
- [ ] Stories carry implementation-ready AC (concrete values, exact error messages, API contracts).
- [ ] `story generate` extracts behaviour from code, not just epic text.
- [ ] Story Ready criteria validated before promotion (`reference-decisions.md`).

## Dependencies

### Blocked By

| Dependency | Type | Status | Owner |
| --- | --- | --- | --- |
| EP0001 | Epic | Ready | Darren Benson |

## Sizing

**Estimated Story Count:** 4

## Story Breakdown

- [ ] US: Epic decomposition + perspectives
- [ ] US: Story creation from epics
- [ ] US: Story generate (brownfield extraction)
- [ ] US: Ready-criteria + quality gate

## Revision History

| Date | Author | Change |
| --- | --- | --- |
| 2026-06-20 | Darren Benson | Epic extracted (brownfield) |
