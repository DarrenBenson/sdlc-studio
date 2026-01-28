<!--
Template: User Story (Streamlined)
File: sdlc-studio/stories/US{NNNN}-{slug}.md
Status values: See reference-outputs.md
Related: help/story.md, reference-story.md
-->
# US{{story_id}}: {{story_title}}

> **Status:** {{status}}
> **Epic:** [EP{{epic_id}}: {{epic_title}}](../epics/EP{{epic_id}}-{{epic_slug}}.md)
> **Owner:** {{owner}}
> **Reviewer:** {{reviewer}}
> **Created:** {{created_date}}

## User Story

**As a** {{persona_name}}
**I want** {{capability}}
**So that** {{benefit}}

## Context

### Persona Reference
**{{persona_name}}** - {{persona_summary}}
[Full persona details](../personas.md#{{persona_anchor}})

### Background
{{background}}

---

## Inherited Constraints

> See Epic for full constraint chain. Key constraints for this story:

| Source | Type | Constraint | AC Implication |
|--------|------|------------|----------------|
| Epic | {{epic_constraint_type}} | {{epic_constraint}} | {{constraint_ac}} |
| PRD | Performance | {{performance_constraint}} | {{performance_ac}} |
| PRD | Security | {{security_constraint}} | {{security_ac}} |

---

## Acceptance Criteria

### AC1: {{ac1_name}}
- **Given** {{ac1_given}}
- **When** {{ac1_when}}
- **Then** {{ac1_then}}

### AC2: {{ac2_name}}
- **Given** {{ac2_given}}
- **When** {{ac2_when}}
- **Then** {{ac2_then}}

### AC3: {{ac3_name}}
- **Given** {{ac3_given}}
- **When** {{ac3_when}}
- **Then** {{ac3_then}}

---

## Scope

### In Scope
- {{in_scope_item}}

### Out of Scope
- {{out_of_scope_item}}

---

## Technical Notes

{{technical_notes}}

### API Contracts
{{api_contracts}}

### Data Requirements
{{data_requirements}}

---

## Edge Cases & Error Handling

| Scenario | Expected Behaviour |
|----------|-------------------|
| {{edge_case}} | {{expected_behaviour}} |

> **Minimum edge cases:** {{config.story_quality.edge_cases.api}} for API stories, {{config.story_quality.edge_cases.other}} for others

---

## Test Scenarios

- [ ] {{test_scenario}}

> **Minimum test scenarios:** {{config.story_quality.test_scenarios.api}} for API stories, {{config.story_quality.test_scenarios.ui}} for UI

---

## Dependencies

### Story Dependencies

| Story | Type | What's Needed | Status |
|-------|------|---------------|--------|
| [US{{dep_story_id}}](US{{dep_story_id}}-{{dep_slug}}.md) | {{type}} | {{what_needed}} | {{status}} |

### External Dependencies

| Dependency | Type | Status |
|------------|------|--------|
| {{dependency}} | {{dependency_type}} | {{dependency_status}} |

---

## Estimation

**Story Points:** {{story_points}}
**Complexity:** {{complexity}}

---

## Open Questions

- [ ] {{question}} - Owner: {{question_owner}}

---

## Revision History

| Date | Author | Change |
|------|--------|--------|
| {{revision_date}} | {{revision_author}} | {{revision_change}} |
