# TSP{{spec_id}}: {{spec_title}}

> **Status:** Draft
> **Epic:** [EP{{epic_id}}: {{epic_title}}](../../epics/EP{{epic_id}}-{{epic_slug}}.md)
> **Created:** {{created_date}}
> **Last Updated:** {{created_date}}

## Overview

{{overview_description}}

## Scope

### Stories Covered

| Story | Title | Priority |
|-------|-------|----------|
{{#each stories}}
| [US{{id}}](../../stories/US{{id}}-{{slug}}.md) | {{title}} | {{priority}} |
{{/each}}

### Test Types Required

| Type | Required | Rationale |
|------|----------|-----------|
| Unit | {{unit_required}} | {{unit_rationale}} |
| Integration | {{integration_required}} | {{integration_rationale}} |
| API | {{api_required}} | {{api_rationale}} |
| E2E | {{e2e_required}} | {{e2e_rationale}} |

## Environment

| Requirement | Details |
|-------------|---------|
| Prerequisites | {{prerequisites}} |
| External Services | {{external_services}} |
| Test Data | {{test_data_requirements}} |

---

## Test Cases

{{#each test_cases}}
### TC{{id}}: {{title}}

**Type:** {{type}}
**Priority:** {{priority}}
**Story:** {{story_ref}}
**Automated:** No

#### Scenario

| Step | Action | Expected Result |
|------|--------|-----------------|
| 1 | Given {{given}} | {{given_result}} |
| 2 | When {{when}} | {{when_result}} |
| 3 | Then {{then}} | {{then_result}} |

#### Test Data

```yaml
input:
  {{input_data}}
expected:
  {{expected_data}}
```

#### Assertions

{{#each assertions}}
- [ ] {{this}}
{{/each}}

---

{{/each}}

## Fixtures

```yaml
# Shared test data for this spec
{{fixtures_yaml}}
```

## Automation Status

| TC | Title | Status | Implementation |
|----|-------|--------|----------------|
{{#each test_cases}}
| TC{{id}} | {{title}} | Pending | - |
{{/each}}

## Traceability

| Artefact | Reference |
|----------|-----------|
| PRD | [sdlc-studio/prd.md](../../prd.md) |
| Epic | [EP{{epic_id}}](../../epics/EP{{epic_id}}-{{epic_slug}}.md) |
| Strategy | [sdlc-studio/testing/strategy.md](../strategy.md) |

## Revision History

| Date | Author | Change |
|------|--------|--------|
| {{created_date}} | {{author}} | Initial spec generation |
