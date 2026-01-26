<!--
Template: User Story
File: sdlc-studio/stories/US{NNNN}-{slug}.md
Status values: See reference-outputs.md
Related: help/story.md, reference-story.md
-->
# US{{story_id}}: {{story_title}}

> **Status:** {{status}}
> **Epic:** [EP{{epic_id}}: {{epic_title}}](../epics/EP{{epic_id}}-{{epic_slug}}.md)
> **Owner:** {{owner}}
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

## Inherited Constraints

Constraints inherited from parent Epic that apply to this Story.

### From Epic

| Type | Constraint | Story Impact |
|------|------------|--------------|
| Risk | {{epic_risk}} | {{risk_handling}} |
| Dependency | {{epic_dependency}} | {{dependency_handling}} |
| Success Metric | {{epic_success_metric}} | {{metric_validation}} |

### From PRD (via Epic)

| Type | Constraint | AC Implication |
|------|------------|----------------|
| Performance | {{inherited_performance}} | {{performance_ac}} |
| Security | {{inherited_security}} | {{security_ac}} |
| Constraint | {{inherited_constraint}} | {{constraint_ac}} |

> **Validation:** Each inherited constraint MUST be addressed in either AC, Edge Cases, or Technical Notes.

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

## Scope

### In Scope

- {{in_scope_item}}

### Out of Scope

- {{out_of_scope_item}}

## UI/UX Requirements

{{ui_requirements}}

## Technical Notes

{{technical_notes}}

### API Contracts

{{api_contracts}}

### Data Requirements

{{data_requirements}}

## Edge Cases & Error Handling

| Scenario | Expected Behaviour |
|----------|-------------------|
| {{edge_case}} | {{expected_behaviour}} |

## Test Scenarios

- [ ] {{test_scenario}}

## Test Cases

| TC ID | Test Case | AC | Type | Status |
|-------|-----------|-----|------|--------|
| [TC{{case_id}}](../testing/cases/TC{{case_id}}-{{case_slug}}.md) | {{case_name}} | AC{{ac_number}} | {{case_type}} | {{case_status}} |

**Feature File:** [{{feature_name}}.feature](../testing/features/{{feature_slug}}.feature)

## Dependencies

### Story Dependencies

| Story | Dependency Type | What's Needed | Status |
|-------|-----------------|---------------|--------|
{{#each story_dependencies}}
| [US{{story_id}}](US{{story_id}}-{{story_slug}}.md) | {{type}} | {{what_needed}} | {{status}} |
{{/each}}

### Schema Dependencies

| Schema | Source Story | Fields Needed |
|--------|--------------|---------------|
{{#each schema_dependencies}}
| {{schema_name}} | [US{{source_story}}](US{{source_story}}-{{source_slug}}.md) | {{fields}} |
{{/each}}

### API Dependencies

| Endpoint | Source Story | How Used |
|----------|--------------|----------|
{{#each api_dependencies}}
| {{endpoint}} | [US{{source_story}}](US{{source_story}}-{{source_slug}}.md) | {{usage}} |
{{/each}}

### External Dependencies

| Dependency | Type | Status |
|------------|------|--------|
| {{dependency}} | {{dependency_type}} | {{dependency_status}} |

{{#if blocked_dependencies}}
> **Warning:** This story depends on stories that are not Done:
{{#each blocked_dependencies}}
> - US{{story_id}}: {{title}} ({{status}})
{{/each}}
{{/if}}

## Estimation

**Story Points:** {{story_points}}

**Complexity:** {{complexity}}

## Open Questions

- [ ] {{question}} - Owner: {{question_owner}}

## Quality Checklist

### API Stories (minimum requirements)

- [ ] Edge cases: {{edge_case_count}}/8 minimum documented
- [ ] Test scenarios: {{test_scenario_count}}/10 minimum listed
- [ ] API contracts: Exact request/response JSON shapes documented
- [ ] Error codes: All error codes with exact messages specified

### All Stories

- [ ] No ambiguous language (avoid: "handles errors", "returns data", "works correctly")
- [ ] Open Questions: {{resolved_count}}/{{total_questions}} resolved (critical must be resolved)
- [ ] Given/When/Then uses concrete values, not placeholders
- [ ] Persona referenced with specific context

### Ready Status Gate

This story can be marked **Ready** when:
- [ ] All critical Open Questions resolved
- [ ] Minimum edge case count met (API stories)
- [ ] No "TBD" placeholders in acceptance criteria
- [ ] Error scenarios documented (not just happy path)

## Revision History

| Date | Author | Change |
|------|--------|--------|
| {{revision_date}} | {{revision_author}} | {{revision_change}} |
