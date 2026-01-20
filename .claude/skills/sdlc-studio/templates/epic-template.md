# EP{{epic_id}}: {{epic_title}}

> **Status:** {{status}}
> **Owner:** {{owner}}
> **Created:** {{created_date}}
> **Target Release:** {{target_release}}

## Summary

{{summary}}

## Inherited Constraints

Constraints that flow from PRD and TRD to this Epic.

### From PRD

| Type | Constraint | Impact on Epic |
|------|------------|----------------|
| Performance | {{prd_performance_requirements}} | {{performance_impact}} |
| Security | {{prd_security_requirements}} | {{security_impact}} |
| Scalability | {{prd_scalability_requirements}} | {{scalability_impact}} |
| Constraint | {{prd_constraint}} | {{constraint_impact}} |

### From TRD

| Type | Constraint | Impact on Epic |
|------|------------|----------------|
| Architecture | {{trd_architecture_pattern}} | {{architecture_impact_detail}} |
| Tech Stack | {{trd_language}}/{{trd_framework}} | {{tech_stack_impact}} |
| Data Model | {{trd_data_constraints}} | {{data_impact}} |

> **Note:** Inherited constraints MUST propagate to child Stories. Check Story templates include these constraints.

## Business Context

### Problem Statement

{{problem_statement}}

**PRD Reference:** [{{prd_section}}](../prd.md#{{prd_anchor}})

### Value Proposition

{{value_proposition}}

### Success Metrics

| Metric | Current State | Target | Measurement Method |
|--------|---------------|--------|-------------------|
| {{metric_name}} | {{current_state}} | {{target}} | {{measurement_method}} |

## Scope

### In Scope

- {{in_scope_item}}

### Out of Scope

- {{out_of_scope_item}}

### Affected User Personas

- **{{persona_name}}:** {{persona_impact}}

## Acceptance Criteria (Epic Level)

- [ ] {{acceptance_criterion}}

## Dependencies

### Blocked By

| Dependency | Type | Status | Owner | Notes |
|------------|------|--------|-------|-------|
| {{dependency}} | {{dependency_type}} | {{dependency_status}} | {{dependency_owner}} | {{dependency_notes}} |

### Blocking

| Item | Type | Impact |
|------|------|--------|
| {{blocking_item}} | {{blocking_type}} | {{blocking_impact}} |

## Risks & Assumptions

### Assumptions

- {{assumption}}

### Risks

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| {{risk_description}} | {{likelihood}} | {{impact}} | {{mitigation}} |

## Technical Considerations

### Architecture Impact

{{architecture_impact}}

### Integration Points

{{integration_points}}

### Data Considerations

{{data_considerations}}

## Sizing & Effort

**Story Points:** {{story_points}}

**Estimated Story Count:** {{story_count}}

**Complexity Factors:**

- {{complexity_factor}}

## Stakeholders

| Role | Name | Interest |
|------|------|----------|
| {{stakeholder_role}} | {{stakeholder_name}} | {{stakeholder_interest}} |

## Story Breakdown

- [ ] [US{{story_id}}: {{story_title}}](../stories/US{{story_id}}-{{story_slug}}.md)

## Test Plan

**Test Plan:** [TP{{plan_id}}: {{plan_title}}](../testing/plans/TP{{plan_id}}-{{plan_slug}}.md)

| Test Suite | Type | Cases | Status |
|------------|------|-------|--------|
| [TS{{suite_id}}](../testing/suites/TS{{suite_id}}-{{suite_slug}}.md) | {{suite_type}} | {{case_count}} | {{suite_status}} |

## Open Questions

- [ ] {{question}} - Owner: {{question_owner}}

## Revision History

| Date | Author | Change |
|------|--------|--------|
| {{revision_date}} | {{revision_author}} | {{revision_change}} |
