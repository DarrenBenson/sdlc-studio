<!--
Template: Epic (Streamlined)
File: sdlc-studio/epics/EP{NNNN}-{slug}.md
Status values: See reference-outputs.md
Modules: epic/engineering-view.md, epic/product-view.md, epic/test-view.md
Related: help/epic.md, reference-epic.md
-->
# EP{{epic_id}}: {{epic_title}}

> **Status:** {{status}}
> **Owner:** {{owner}}
> **Reviewer:** {{reviewer}}
> **Created:** {{created_date}}
> **Target Release:** {{target_release}}

## Summary

{{summary}}

## Inherited Constraints

> See PRD and TRD for full constraint details. Key constraints for this epic:

| Source | Type | Constraint | Impact |
|--------|------|------------|--------|
| PRD | Performance | {{prd_performance}} | {{performance_impact}} |
| PRD | Security | {{prd_security}} | {{security_impact}} |
| TRD | Architecture | {{trd_architecture}} | {{architecture_impact}} |
| TRD | Tech Stack | {{trd_stack}} | {{stack_impact}} |

---

## Business Context

### Problem Statement
{{problem_statement}}

**PRD Reference:** [{{prd_section}}](../prd.md#{{prd_anchor}})

### Value Proposition
{{value_proposition}}

### Success Metrics

| Metric | Current | Target | Measurement |
|--------|---------|--------|-------------|
| {{metric_name}} | {{current}} | {{target}} | {{method}} |

---

## Scope

### In Scope
- {{in_scope_item}}

### Out of Scope
- {{out_of_scope_item}}

### Affected Personas
- **{{persona_name}}:** {{persona_impact}}

---

## Acceptance Criteria (Epic Level)

- [ ] {{acceptance_criterion}}

---

## Dependencies

### Blocked By

| Dependency | Type | Status | Owner |
|------------|------|--------|-------|
| {{dependency}} | {{type}} | {{status}} | {{owner}} |

### Blocking

| Item | Type | Impact |
|------|------|--------|
| {{blocking_item}} | {{type}} | {{impact}} |

---

## Risks & Assumptions

### Assumptions
- {{assumption}}

### Risks

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| {{risk}} | {{likelihood}} | {{impact}} | {{mitigation}} |

---

## Technical Considerations

### Architecture Impact
{{architecture_impact}}

### Integration Points
{{integration_points}}

---

## Sizing

**Story Points:** {{story_points}}
**Estimated Story Count:** {{story_count}}

**Complexity Factors:**
- {{complexity_factor}}

---

## Story Breakdown

- [ ] [US{{story_id}}: {{story_title}}](../stories/US{{story_id}}-{{story_slug}}.md)

---

## Test Plan

**Test Spec:** [TS{{spec_id}}: {{spec_title}}](../test-specs/TS{{spec_id}}-{{spec_slug}}.md)

---

## Open Questions

- [ ] {{question}} - Owner: {{question_owner}}

---

## Revision History

| Date | Author | Change |
|------|--------|--------|
| {{revision_date}} | {{revision_author}} | {{revision_change}} |
